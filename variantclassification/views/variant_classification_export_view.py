from urllib.parse import unquote_plus

from django.conf import settings
from django.db.models import QuerySet
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseBase
from django.shortcuts import render
from django.urls.base import reverse
from htmlmin.decorators import not_minified_response
from pytz import timezone
from requests.models import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from typing import List

from library.django_utils import get_url_from_view_path
from library.log_utils import report_event
from snpdb.models.models import Lab, Organization
from snpdb.models.models_genome import GenomeBuild
from snpdb.models.models_user_settings import UserSettings
from variantclassification.enums.variant_classification_enums import ShareLevel
from variantclassification.models.variant_classification import VariantClassificationModification
from variantclassification.models.variant_classification_ref import VariantClassificationRef
from variantclassification.views.variant_classification_export_clinvar import ExportFormatterClinvar
from variantclassification.views.variant_classification_export_csv import ExportFormatterCSV
from variantclassification.views.variant_classification_export_json import ExportFormatterJSON
from variantclassification.views.variant_classification_export_keys import ExportFormatterKeys
from variantclassification.views.variant_classification_export_mvl import ExportFormatterMVL
from variantclassification.views.variant_classification_export_mvl_shell import ExportFormatterMVLShell
from variantclassification.views.variant_classification_export_redcap import ExportFormatterRedcap, \
    export_redcap_definition
from variantclassification.views.variant_classification_export_report import ExportFormatterReport
from variantclassification.views.variant_classification_export_utils import ConflictStrategy, \
    VCFEncoding, BaseExportFormatter
from variantclassification.views.variant_classification_export_vcf import ExportFormatterVCF


def export_view(request: HttpRequest) -> Response:

    orgs = Organization.objects.all().filter(active=True, group_name__isnull=False).order_by('group_name')
    labs = Lab.objects.all().filter(organization__active=True, group_name__isnull=False).order_by('group_name')

    genome_builds = GenomeBuild.objects.all()

    user_settings = UserSettings.get_for_user(request.user)
    format_keys = {'id': 'keys', 'name': 'Evidence Keys Report', 'admin_only': True}
    format_mvl = {'id': 'mvl', 'name': 'MVL'}
    format_csv = {'id': 'csv', 'name': 'CSV'}
    format_clinvar_xml = {'id': 'clinvar', 'name': 'Clinvar XML', 'admin_only': True}
    format_json = {'id': 'json', 'name': 'JSON'}
    format_redcap = {'id': 'redcap', 'name': 'REDCap'}
    format_vcf = {'id': 'vcf', 'name': 'VCF'}
    #format_errors = {'id': 'errors', 'name': 'Liftover Errors'}
    formats = [
        format_clinvar_xml,
        format_keys,
        format_csv,
        format_json,
        format_mvl,
        format_redcap,
        format_vcf,
    #    format_errors
    ]

    context = {
        'labs': labs,
        'orgs': orgs,
        'genome_builds': genome_builds,
        'default_genome_build': user_settings.default_genome_build,
        'formats': formats,
        'default_format': format_csv,
        'base_url': get_url_from_view_path(reverse('variant_classification_export_api')),
        'base_url_redirect': get_url_from_view_path(reverse('variant_classification_export_redirect'))
    }

    return render(request, 'variantclassification/variant_classification_export.html', context)


def export_view_redirector(request: HttpRequest) -> Response:
    query_string = request.GET.urlencode()
    all_params = dict([(key, unquote_plus(value)) for key, value in request.GET.dict().items()])

    share_level = all_params.pop('share_level', None)
    build = all_params.pop('build', None)
    exclude_orgs = all_params.pop('exclude_orgs', None)
    exclude_labs = all_params.pop('exclude_labs', None)
    include_labs = all_params.pop('include_labs', None)

    exclude_list = []
    include_list = []
    if exclude_orgs:
        for org_group in [o.strip() for o in exclude_orgs.split(',')]:
            try:
                org_name = Organization.objects.get(group_name=org_group).name
                exclude_list.append(org_name)
            except:
                exclude_list.append(f'Unknown org : {org_group}')

    def to_lab_names(lab_string) -> List[str]:
        lab_list = []
        if lab_string:
            for lab_group in [l.strip() for l in lab_string.split(',')]:
                try:
                    lab_name = Lab.objects.get(group_name=lab_group).name
                    lab_list.append(lab_name)
                except:
                    lab_list.append(f'Unknown lab : {lab_group}')
        return lab_list

    exclude_list += to_lab_names(exclude_labs)
    include_list += to_lab_names(include_labs)

    include_details = 'All'
    if include_list:
        include_details = f'Only from {", ".join(include_list)}'
    elif exclude_list:
        include_details = f'Exclude {", ".join(exclude_list)}'

    format = all_params.pop('type', None)
    the_rest = all_params

    context = {
        'query_string': query_string,
        'share_level': share_level,
        'build': build,
        'include_details': include_details,
        'format': format,
        'the_rest': the_rest
    }
    return render(request, 'variantclassification/variant_classification_export_redirect.html', context)


class VariantClassificationApiExportView(APIView):

    @staticmethod
    def string_to_labs(lab_str: str) -> List[Lab]:
        parts = [l.strip() for l in lab_str.split(',')]
        labs = [Lab.objects.filter(group_name=lab_str).first() for lab_str in parts]
        labs = [l for l in labs if l]
        return labs

    @staticmethod
    def string_to_orgs(lab_str: str) -> List[Organization]:
        parts = [l.strip() for l in lab_str.split(',')]
        orgs = [Organization.objects.filter(group_name=lab_str).first() for lab_str in parts]
        orgs = [o for o in orgs if o]
        return orgs

    def get(self, request: Request, **kwargs) -> HttpResponseBase:

        build_name = request.query_params.get('build', 'GRCh38')
        share_level = request.query_params.get('share_level', 'public')
        genome_build = GenomeBuild.get_name_or_alias(build_name)
        pretty = request.query_params.get('value_format') == 'labels'

        file_format = request.query_params.get('type', 'csv')
        conflict_strategy = request.query_params.get('conflict_strategy', ConflictStrategy.MOST_PATHOGENIC)
        encoding = request.query_params.get('encoding', VCFEncoding.BASIC)
        cs_override_labels = {}
        for key in ['b', 'lb', 'vus', 'lp', 'p']:
            cs_label = request.query_params.get(f'cs_{key}')
            if cs_label:
                cs_override_labels[key.upper()] = cs_label

        qs = VariantClassificationModification.objects.filter(is_last_published=True)
        # don't include withdrawn records in any export
        qs = qs.exclude(variant_classification__withdrawn=True)

        # so the below looks a little switched around but is currently correct
        # the parameter share_level of 'public' should be changed to 'app_users'
        if share_level == 'public':
            qs = qs.filter(share_level__in=ShareLevel.DISCORDANT_LEVEL_KEYS)
        elif share_level == '3rd_party':
            qs = qs.filter(share_level=ShareLevel.PUBLIC)

        # always restrict to user for security reasons (even if possibly redundant)
        qs = VariantClassificationModification.filter_for_user(request.user, qs)

        exclude_labs = request.query_params.get('exclude_labs', None)
        include_labs = request.query_params.get('include_labs', None)
        exclude_orgs = request.query_params.get('exclude_orgs', None)

        if include_labs:
            include_lab_array = VariantClassificationApiExportView.string_to_labs(include_labs)
            qs = qs.filter(variant_classification__lab__in=include_lab_array)
        if exclude_labs:
            exclude_lab_array = VariantClassificationApiExportView.string_to_labs(exclude_labs)
            qs = qs.exclude(variant_classification__lab__in=exclude_lab_array)
        if exclude_orgs:
            exclude_org_array = VariantClassificationApiExportView.string_to_orgs(exclude_orgs)
            qs = qs.exclude(variant_classification__lab__organization__in=exclude_org_array)

        if file_format == 'mvl':
            transcript_strategy = request.query_params.get('transcript_strategy', 'refseq')
            if transcript_strategy == 'refseq':
                # exclude ensembl transcripts
                qs = qs.exclude(published_evidence__c_hgvs__value__startswith='ENS')

        formatter: BaseExportFormatter
        qs = qs.select_related('variant_classification', 'variant_classification__lab')

        formatter_kwargs = {
            "genome_build": genome_build,
            "qs": qs,
            "user": request.user,
        }
        report_event(
            name='variant classification download',
            request=request,
            extra_data={
                'format': file_format,
                'approx_count': qs.count(),
                'refer': 'download page'
            }
        )

        if file_format == 'mvl':
            if request.query_params.get('mvl_detail', 'standard') == 'shell':
                formatter = ExportFormatterMVLShell(conflict_strategy=conflict_strategy,
                                               cs_override_labels=cs_override_labels, **formatter_kwargs)
            else:
                formatter = ExportFormatterMVL(conflict_strategy=conflict_strategy, cs_override_labels=cs_override_labels, **formatter_kwargs)
        elif file_format == 'json':
            formatter = ExportFormatterJSON(**formatter_kwargs)
        elif file_format == 'redcap':
            formatter = ExportFormatterRedcap(**formatter_kwargs)
        elif file_format == 'vcf':
            formatter = ExportFormatterVCF(encoding=encoding, **formatter_kwargs)
        elif file_format == 'csv':
            formatter = ExportFormatterCSV(pretty=pretty, **formatter_kwargs)
        elif file_format == 'clinvar':
            formatter = ExportFormatterClinvar(**formatter_kwargs)
        elif file_format == 'keys':
            formatter = ExportFormatterKeys(qs=qs)

        else:
            raise ValueError(f'Unexpected file format {file_format}')

        return formatter.export()


def _single_classification_mod_qs(request, record_id) -> QuerySet:
    vcm = VariantClassificationRef.init_from_obj(request.user, record_id).modification
    qs = VariantClassificationModification.objects.filter(pk=vcm.id)
    return qs


def clinvar_xml(request, record_id) -> HttpResponseBase:
    report_event(
        name='variant classification download',
        request=request,
        extra_data={
            'format': 'clinvar',
            'record_id': record_id,
            'refer': 'classification form',
            'approx_count': 1
        }
    )

    vcm = VariantClassificationRef.init_from_obj(request.user, record_id).modification
    qs = _single_classification_mod_qs(request, record_id)
    genome_build = UserSettings.get_for_user(request.user).default_genome_build

    start_part = vcm.variant_classification.friendly_label.replace('/', '-')
    date_part = str(vcm.created.astimezone(tz=timezone(settings.TIME_ZONE)).strftime("%Y-%m-%d"))
    filename = f'{start_part} - {date_part} clinvar.xml'
    return ExportFormatterClinvar(user=request.user, filename_override=filename, genome_build=genome_build, qs=qs).export(as_attachment=False)

@not_minified_response
def template_report(request, record_id) -> HttpResponseBase:
    qs = _single_classification_mod_qs(request, record_id)
    genome_build = UserSettings.get_for_user(request.user).default_genome_build

    return ExportFormatterReport(user=request.user, genome_build=genome_build, qs=qs).export(as_attachment=False)


def redcap_data_dictionary(request) -> HttpResponseBase:
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="redcap_data_definition.csv"'
    export_redcap_definition(response)
    return response


def record_csv(request, record_id) -> HttpResponseBase:
    report_event(
        name='variant classification download',
        request=request,
        extra_data={
            'format': 'csv',
            'record_id': record_id,
            'refer': 'classification form',
            'approx_count': 1
        }
    )
    vcm: VariantClassificationModification = VariantClassificationRef.init_from_obj(request.user, record_id).modification
    qs = VariantClassificationModification.objects.filter(pk=vcm.id)

    genome_build = UserSettings.get_for_user(request.user).default_genome_build
    start_part = vcm.variant_classification.friendly_label.replace('/', '-')
    date_part = str(vcm.created.astimezone(tz=timezone(settings.TIME_ZONE)).strftime("%Y-%m-%d"))
    filename = f'{start_part} - {date_part}.csv'
    ef = ExportFormatterCSV(user=request.user, filename_override=filename, genome_build=genome_build, qs=qs)
    return ef.export()
