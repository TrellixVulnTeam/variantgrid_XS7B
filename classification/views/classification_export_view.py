import operator
import re
from datetime import datetime, timedelta
from functools import reduce
from typing import List
from urllib.parse import unquote_plus

from django.conf import settings
from django.db.models import QuerySet, Q
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseBase
from django.shortcuts import render
from django.urls.base import reverse
from django.utils import timezone
from htmlmin.decorators import not_minified_response
from requests.models import Response
from rest_framework.request import Request
from rest_framework.views import APIView

from classification.enums.classification_enums import ShareLevel
from classification.models.classification import ClassificationModification
from classification.models.classification_ref import ClassificationRef
from classification.views.classification_export_json import ExportFormatterJSON
from classification.views.classification_export_keys import ExportFormatterKeys
from classification.views.classification_export_redcap import ExportFormatterRedcap, \
    export_redcap_definition
from classification.views.classification_export_report import ExportFormatterReport
from classification.views.classification_export_utils import ConflictStrategy, \
    VCFEncoding, BaseExportFormatter
from classification.views.classification_export_vcf import ExportFormatterVCF
from classification.views.exports import ClassificationExportFormatter2CSV
from classification.views.exports.classification_export_decorator import UnsupportedExportType
from classification.views.exports.classification_export_filter import ClassificationFilter
from classification.views.exports.classification_export_formatter2_csv import FormatDetailsCSV
from classification.views.exports.classification_export_view import serve_export
from library.django_utils import get_url_from_view_path
from snpdb.genome_build_manager import GenomeBuildManager
from snpdb.models.models import Lab, Organization
from snpdb.models.models_genome import GenomeBuild
from snpdb.models.models_user_settings import UserSettings

ALISSA_ACCEPTED_TRANSCRIPTS = {"NM_", "NR_"}


def parse_since(since_str: str) -> datetime:
    try:
        since_date = datetime.strptime(since_str, '%Y-%m-%d').replace(tzinfo=timezone.get_current_timezone())
        since_date = since_date.replace(minute=0, hour=0, second=0, microsecond=0)
        return since_date
    except BaseException:
        pass

    if m := re.compile(r"([0-9]+)(\w*)").match(since_str):
        amount = int(m.group(1))
        unit = m.group(2)
        if unit:
            unit = unit.strip().lower()

        if amount > 100000 and not unit:
            return datetime.utcfromtimestamp(float(since_str)).replace(tzinfo=timezone.utc)

        since = datetime.utcnow().replace(tzinfo=timezone.utc)
        if not unit or unit == 'd':
            since -= timedelta(days=amount)
        elif unit == 'm':
            since -= timedelta(minutes=amount)
        elif unit == 'w':
            since -= timedelta(weeks=amount)
        elif unit == 's':
            since -= timedelta(seconds=amount)
        else:
            raise ValueError(f"Cannot parse {since_str} don't know time unit {unit}")
        return since

    try:
        return datetime.utcfromtimestamp(float(since_str)).replace(tzinfo=timezone.utc)
    except BaseException:
        pass

    raise ValueError(f"Could not parse since string {since_str}")


def export_view(request: HttpRequest) -> Response:

    orgs = Organization.objects.filter(active=True, group_name__isnull=False).order_by('group_name')
    labs = Lab.objects.filter(organization__active=True, group_name__isnull=False).order_by('group_name')

    genome_builds = GenomeBuild.objects.all()

    user_settings = UserSettings.get_for_user(request.user)
    format_keys = {'id': 'keys', 'name': 'Evidence Keys Report', 'admin_only': True}
    format_mvl = {'id': 'mvl', 'name': 'MVL'}
    format_csv = {'id': 'csv', 'name': 'CSV'}
    format_clinvar_compare = {'id': 'clinvar_compare', 'name': 'ClinVar Compare', 'admin_only': True}
    format_json = {'id': 'json', 'name': 'JSON'}
    format_spelling = {'id': 'spelling', 'name': 'Spelling Report', 'admin_only': True}
    format_redcap = {'id': 'redcap', 'name': 'REDCap'}
    format_vcf = {'id': 'vcf', 'name': 'VCF'}
    formats = [
        format_keys,
        format_csv,
        format_clinvar_compare,
        format_spelling,
        format_json,
        format_mvl
    ]
    if settings.VARIANT_CLASSIFICATION_REDCAP_EXPORT:
        formats += [format_redcap]

    formats += [
        format_vcf
    ]

    context = {
        'labs': labs,
        'orgs': orgs,
        'genome_builds': genome_builds,
        'default_genome_build': user_settings.default_genome_build,
        'formats': formats,
        'default_format': format_csv,
        'base_url': get_url_from_view_path(reverse('classification_export_api')),
        'base_url_redirect': get_url_from_view_path(reverse('classification_export_redirect'))
    }

    return render(request, 'classification/classification_export.html', context)


def export_view_redirector(request: HttpRequest) -> Response:
    query_string = request.GET.urlencode()
    all_params = dict([(key, unquote_plus(value)) for key, value in request.GET.dict().items()])

    share_level = all_params.pop('share_level', None)
    build = all_params.pop('build', None)
    exclude_orgs = all_params.pop('exclude_orgs', None)
    exclude_labs = all_params.pop('exclude_labs', None)
    include_labs = all_params.pop('include_labs', None)
    since_str = all_params.pop('since', None)
    if since_str:
        since = parse_since(since_str).astimezone(timezone.get_default_timezone())
        since_str = since_str + " -> " + since.strftime("%Y-%m-%d %H:%M:%S %z")
    else:
        since_str = 'All'

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
        'since': since_str,
        'the_rest': the_rest
    }
    return render(request, 'classification/classification_export_redirect.html', context)


class ClassificationApiExportView(APIView):

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

        file_format = request.query_params.get('type')

        try:
            return serve_export(request)
        except UnsupportedExportType:
            # assume that the default import will handle it if type wasn't handled elsewhere
            pass

        # deprecating all this... eventually

        since = None
        since_str = request.query_params.get('since', None)
        if since_str:
            since = parse_since(since_str)

        build_name = request.query_params.get('build', 'GRCh38')
        share_level = request.query_params.get('share_level', 'public')
        genome_build = GenomeBuild.get_name_or_alias(build_name)
        pretty = request.query_params.get('value_format') == 'labels'

        conflict_strategy = request.query_params.get('conflict_strategy', ConflictStrategy.MOST_PATHOGENIC)
        encoding = request.query_params.get('encoding', VCFEncoding.BASIC)
        cs_override_labels = {}
        for key in ['b', 'lb', 'vus', 'lp', 'p']:
            cs_label = request.query_params.get(f'cs_{key}')
            if cs_label:
                cs_override_labels[key.upper()] = cs_label

        qs = ClassificationModification.objects.filter(is_last_published=True)
        # only include excluded if we have a since and need to report deltas of records being withdrawn
        if not since:
            qs = qs.exclude(classification__withdrawn=True)

        # so the below looks a little switched around but is currently correct
        # the parameter share_level of 'public' should be changed to 'app_users'
        if share_level == 'public':
            qs = qs.filter(share_level__in=ShareLevel.DISCORDANT_LEVEL_KEYS)
        elif share_level == '3rd_party':
            qs = qs.filter(share_level=ShareLevel.PUBLIC)

        # always restrict to user for security reasons (even if possibly redundant)
        qs = ClassificationModification.filter_for_user(request.user, qs)

        exclude_labs = request.query_params.get('exclude_labs', None)
        include_labs = request.query_params.get('include_labs', None)
        exclude_orgs = request.query_params.get('exclude_orgs', None)

        if include_labs:
            include_lab_array = ClassificationApiExportView.string_to_labs(include_labs)
            qs = qs.filter(classification__lab__in=include_lab_array)
        if exclude_labs:
            exclude_lab_array = ClassificationApiExportView.string_to_labs(exclude_labs)
            qs = qs.exclude(classification__lab__in=exclude_lab_array)
        if exclude_orgs:
            exclude_org_array = ClassificationApiExportView.string_to_orgs(exclude_orgs)
            qs = qs.exclude(classification__lab__organization__in=exclude_org_array)

        if file_format == 'mvl':
            transcript_strategy = request.query_params.get('transcript_strategy', 'refseq')
            if transcript_strategy == 'refseq':
                # exclude non NC/NR/NX transcripts
                acceptable_transcripts: List[Q] = [
                    Q(published_evidence__c_hgvs__value__startswith=tran) for tran in ALISSA_ACCEPTED_TRANSCRIPTS
                ]
                qs = qs.filter(reduce(operator.or_, acceptable_transcripts))

        formatter: BaseExportFormatter
        qs = qs.select_related(
            'classification',
            'classification__lab',
            'classification__lab__organization',
            'classification__clinical_context',
            'classification__allele',
            'classification__allele__clingen_allele',
            'classification__flag_collection')

        if allele := request.query_params.get('allele'):
            qs = qs.filter(classification__allele_id=int(allele))

        formatter_kwargs = {
            "genome_build": genome_build,
            "qs": qs,
            "user": request.user,
            "since": since
        }

        if file_format == 'json':
            formatter = ExportFormatterJSON(**formatter_kwargs)
        elif file_format == 'redcap':
            formatter = ExportFormatterRedcap(**formatter_kwargs)
        elif file_format == 'vcf':
            formatter = ExportFormatterVCF(encoding=encoding, **formatter_kwargs)
        elif file_format == 'keys':
            formatter = ExportFormatterKeys(qs=qs)
        else:
            raise ValueError(f'Unsupported export format {file_format}')

        if request.query_params.get('benchmark') == 'true':
            benchmarks = formatter.benchmark()
            return render(request, "snpdb/benchmark.html", {"content": benchmarks})

        return formatter.export()


def _single_classification_mod_qs(request: HttpRequest, record_id) -> QuerySet:
    vcm = ClassificationRef.init_from_obj(request.user, record_id).modification
    qs = ClassificationModification.objects.filter(pk=vcm.id)
    return qs


@not_minified_response
def template_report(request: HttpRequest, classification_id) -> HttpResponseBase:
    qs = _single_classification_mod_qs(request, classification_id)
    genome_build = UserSettings.get_for_user(request.user).default_genome_build

    return ExportFormatterReport(user=request.user, genome_build=genome_build, qs=qs).export(as_attachment=False)


def redcap_data_dictionary(request: HttpRequest) -> HttpResponseBase:
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="redcap_data_definition.csv"'
    export_redcap_definition(response)
    return response


def record_csv(request: HttpRequest, classification_id) -> HttpResponseBase:
    vcm: ClassificationModification = ClassificationRef.init_from_obj(request.user, classification_id).modification
    qs = ClassificationModification.objects.filter(pk=vcm.id)

    filename_parts = [
        vcm.classification.lab.group_name.replace('/', '-'),
        vcm.classification.lab_record_id.replace('/', '-'),
        str(vcm.created.astimezone(tz=timezone.get_default_timezone()).strftime("%Y-%m-%d"))
    ]
    file_prefix = "_".join(filename_parts)

    return ClassificationExportFormatter2CSV(
        ClassificationFilter(
            user=request.user,
            genome_build=GenomeBuildManager.get_current_genome_build(),
            starting_query=qs,
            file_prefix=file_prefix
        ),
        FormatDetailsCSV()
    ).serve()
