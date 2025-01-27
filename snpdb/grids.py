import operator
from functools import reduce

from django.conf import settings
from django.db.models import F
from django.db.models.aggregates import Count
from django.db.models.query_utils import Q
from guardian.shortcuts import get_objects_for_user

from library.database_utils import get_queryset_column_names, \
    get_queryset_select_from_where_parts
from library.jqgrid_sql import JqGridSQL
from library.jqgrid_user_row_config import JqGridUserRowConfig
from library.utils import calculate_age
from snpdb.grid_columns.custom_columns import get_variantgrid_extra_alias_and_select_columns
from snpdb.models import VCF, Cohort, Sample, ImportStatus, \
    GenomicIntervalsCollection, CustomColumnsCollection, Variant, Trio, UserGridConfig, GenomeBuild
from snpdb.tasks.soft_delete_tasks import soft_delete_vcfs, remove_soft_deleted_vcfs_task


class VCFListGrid(JqGridUserRowConfig):
    model = VCF
    caption = 'VCFs'
    fields = ["id", "name", "date", "import_status", "genome_build__name", "user__username", "source",
              "uploadedvcf__uploaded_file__import_source", "genotype_samples", "project__name", "cohort__import_status",
              "uploadedvcf__vcf_importer__name", 'uploadedvcf__vcf_importer__version']
    colmodel_overrides = {
        'id': {"hidden": True},
        "name": {'width': 550,
                 'formatter': 'viewVCFLink',
                 'formatter_kwargs': {"icon_css_class": "vcf-icon",
                                      "url_name": "view_vcf",
                                      "url_object_column": "id"}},
        'import_status': {'formatter': 'viewImportStatus'},
        "genome_build__name": {"label": "Genome Build"},
        'user__username': {'label': 'Uploaded by', 'width': 60},
        'source': {'label': 'VCF source'},
        "project__name": {'label': "Project"},
        'cohort__import_status': {'hidden': True},
        'uploadedvcf__vcf_importer__name': {"label": 'VCF Importer', "hide_non_admin": True},
        'uploadedvcf__vcf_importer__version': {"label": 'VCF Importer Version', "hide_non_admin": True},
    }

    def __init__(self, user, **kwargs):
        extra_filters = kwargs.get("extra_filters")
        super().__init__(user)
        user_grid_config = UserGridConfig.get(user, self.caption)
        queryset = VCF.filter_for_user(user, group_data=user_grid_config.show_group_data)

        # Set via vcf_grid_filter_tags
        if extra_filters:
            if project := extra_filters.get("project"):
                queryset = queryset.filter(project=project)
            if genome_build_name := extra_filters.get("genome_build_name"):
                genome_build = GenomeBuild.get_name_or_alias(genome_build_name)
                queryset = queryset.filter(genome_build=genome_build)

        self.queryset = queryset.order_by("-pk").values(*self.get_field_names())
        self.extra_config.update({'shrinkToFit': False,
                                  'sortname': 'id',
                                  'sortorder': 'desc'})

    def delete_row(self, vcf_id):
        """ Do async as it may be slow """
        soft_delete_vcfs(self.user, vcf_id)


# TODO: Merge this an cohort grid below into 1
class SamplesListGrid(JqGridUserRowConfig):
    model = Sample
    caption = 'Samples'
    fields = ["id", "name", "het_hom_count", "vcf__date", "import_status", "vcf__genome_build__name", "variants_type",
              "vcf__user__username", "vcf__source", "vcf__name", "vcf__project__name", "vcf__uploadedvcf__uploaded_file__import_source",
              "sample_gene_list_count", "activesamplegenelist__id",
              "mutationalsignature__id", "mutationalsignature__summary",
              "somaliersampleextract__somalierancestry__predicted_ancestry",
              "patient__first_name", "patient__last_name", "patient__sex",
              "patient__date_of_birth", "patient__date_of_death",
              "specimen__reference_id", "specimen__tissue__name", "specimen__collection_date", "vcf__id"]
    colmodel_overrides = {
        'id': {"hidden": True},
        "name": {"width": 400,
                 'formatter': 'viewSampleLink',
                 'formatter_kwargs': {"icon_css_class": "sample-icon",
                                      "url_name": "view_sample",
                                      "url_object_column": "id"}},
        'import_status': {'formatter': 'viewImportStatus'},
        'vcf__id': {"hidden": True},
        "vcf__genome_build__name": {"label": "Genome Build"},
        'vcf__source': {'label': 'VCF source'},
        'vcf__name': {
            'label': 'VCF Name', "width": 600,
            "formatter": 'linkFormatter',
            'formatter_kwargs': {"icon_css_class": "vcf-icon",
                                 "url_name": "view_vcf",
                                 "url_object_column": "vcf__id"}
        },
        "vcf__project__name": {'label': "Project"},
        "sample_gene_list_count": {'name': 'sample_gene_list_count', 'label': '# Sample GeneLists',
                                   "model_field": False, "formatter": "viewSampleGeneList", 'sorttype': 'int'},
        'activesamplegenelist__id': {'hidden': True},
        'mutationalsignature__id': {'hidden': True},
        'mutationalsignature__summary': {'label': 'Mutational Signature',
                                         'formatter': 'viewMutationalSignature'},
        "somaliersampleextract__somalierancestry__predicted_ancestry": {"label": "Predicted Ancestry"},
        'patient__last_name': {'label': 'Last Name'},
        'patient__sex': {'label': 'Sex'},
        'patient__date_of_birth': {'label': 'D.O.B.'},
        'patient__date_of_death': {'hidden': True},
        'het_hom_count': {'name': 'het_hom_count', "model_field": False, 'sorttype': 'int',
                          'label': 'Het/Hom Count'},
        "specimen__reference_id": {'label': 'Specimen'}
    }

    def __init__(self, user, **kwargs):
        extra_filters = kwargs.get("extra_filters")
        super().__init__(user)

        user_grid_config = UserGridConfig.get(user, self.caption)
        queryset = Sample.filter_for_user(user, group_data=user_grid_config.show_group_data)

        # Set via vcf_grid_filter_tags
        if extra_filters:
            if project := extra_filters.get("project"):
                queryset = queryset.filter(vcf__project=project)
            if genome_build_name := extra_filters.get("genome_build_name"):
                genome_build = GenomeBuild.get_name_or_alias(genome_build_name)
                queryset = queryset.filter(vcf__genome_build=genome_build)
            variants_type = extra_filters.get("variants_type")
            if variants_type is not None:
                queryset = queryset.filter(variants_type__in=variants_type)

        # If you don't have permission to view a patient - blank it out
        # If you have read only and
        # TODO: We need to pass whole row in - as we need date of death to display age
        if settings.PATIENTS_READ_ONLY_SHOW_AGE_NOT_DOB:
            dob_colmodel = self._overrides.get('patient__date_of_birth', {})
            dob_colmodel['label'] = "Age"
            dob_colmodel['server_side_formatter'] = lambda row, field: calculate_age(row[field])
            self._overrides['patient__date_of_birth'] = dob_colmodel

        # Only show mut sig column if we have any
        if not queryset.filter(mutationalsignature__isnull=False).exists():
            mut_sig_colmodel = self._overrides.get('mutationalsignature__summary', {})
            mut_sig_colmodel['hidden'] = True
            self._overrides['mutationalsignature__summary'] = mut_sig_colmodel

        if not queryset.filter(somaliersampleextract__somalierancestry__isnull=False).exists():
            somalier_ancestry_colmodel = self._overrides.get('somaliersampleextract__somalierancestry__predicted_ancestry', {})
            somalier_ancestry_colmodel['hidden'] = True
            self._overrides['somaliersampleextract__somalierancestry__predicted_ancestry'] = somalier_ancestry_colmodel

        if not queryset.filter(samplegenelist__isnull=False).exists():
            sample_gene_list_count = self._overrides.get('sample_gene_list_count', {})
            sample_gene_list_count['hidden'] = True
            self._overrides['sample_gene_list_count'] = sample_gene_list_count

        annotation_kwargs = {
            "sample_gene_list_count": Count("samplegenelist", distinct=True),
            "het_hom_count": F("samplestats__het_count") + F("samplestats__hom_count"),
        }
        queryset = queryset.annotate(**annotation_kwargs)
        self.queryset = queryset.order_by("-pk").values(*self.get_field_names())
        self.extra_config.update({'shrinkToFit': False,
                                  'sortname': 'id',
                                  'sortorder': 'desc'})

    def delete_row(self, sample_id):
        """ Do async as it may take a few secs to delete """

        sample = Sample.get_for_user(self.user, sample_id)
        sample.check_can_write(self.user)
        Sample.objects.filter(pk=sample.pk).update(import_status=ImportStatus.MARKED_FOR_DELETION)
        task = remove_soft_deleted_vcfs_task.si()  # @UndefinedVariable
        task.apply_async()


class CohortSampleListGrid(JqGridUserRowConfig):
    model = Sample
    caption = 'Cohort Samples'
    fields = ["id", "name", "vcf__name", "patient__family_code",
              "patient__first_name", "patient__first_name",
              "patient__sex", "patient__date_of_birth"]
    colmodel_overrides = {'id': {'width': 20, 'formatter': 'viewSampleLink'},
                          'vcf__name': {'label': 'VCF'},
                          'patient__family_code': {'label': 'Family Code'},
                          'patient__first_name': {'label': 'First Name'},
                          'patient__last_name': {'label': 'Last Name'},
                          'patient__sex': {'label': 'Sex'},
                          'patient__date_of_birth': {'label': 'D.O.B.'}}

    def __init__(self, user, cohort_id, extra_filters=None):
        super().__init__(user)

        if extra_filters is None:
            extra_filters = {}

        cohort = Cohort.get_for_user(user, cohort_id)
        sample_filters = [Q(vcf__genome_build=cohort.genome_build),
                          Q(import_status=ImportStatus.SUCCESS)]
        SHOW_COHORT = "show_cohort"
        EXCLUDE_COHORT = "exclude_cohort"
        cohort_op = extra_filters.get("cohort_op", EXCLUDE_COHORT)
        cohort_q = Q(cohortsample__cohort=cohort)
        if cohort_op == SHOW_COHORT:
            pass
        elif cohort_op == EXCLUDE_COHORT:
            cohort_q = ~cohort_q
        else:
            raise ValueError(f"Unknown cohort_op: '{cohort_op}'")

        sample_filters.append(cohort_q)
        q = reduce(operator.and_, sample_filters)
        queryset = Sample.filter_for_user(user).filter(q).order_by("-pk")
        self.queryset = queryset.values(*self.get_field_names())


class CohortListGrid(JqGridUserRowConfig):
    model = Cohort
    caption = 'Cohorts'
    fields = ["id", "name", "import_status", "user__username", "modified", "sample_count"]
    colmodel_overrides = {
        'id': {"hidden": True},
        "name": {'formatter': 'linkFormatter',
                 'formatter_kwargs': {"icon_css_class": "cohort-icon",
                                      "url_name": "view_cohort",
                                      "url_object_column": "id"}},
        "sample_count": {"label": "Sample Count"},
    }

    def __init__(self, user):
        super().__init__(user)
        user_grid_config = UserGridConfig.get(user, self.caption)
        queryset = self.model.filter_for_user(user, success_status_only=False)
        if not user_grid_config.show_group_data:
            queryset = queryset.filter(user=user)
        queryset = queryset.filter(vcf__isnull=True)  # Don't show auto-cohorts

        self.queryset = queryset.values(*self.get_field_names())
        self.extra_config.update({'sortname': "modified",
                                  'sortorder': "desc"})


class TriosListGrid(JqGridUserRowConfig):
    model = Trio
    caption = 'Trios'
    fields = ["id", "name", "user__username", "modified", "mother__sample__name", "mother_affected",
              "father__sample__name", "father_affected", "proband__sample__name"]
    colmodel_overrides = {
        'id': {'formatter': 'linkFormatter',
               'formatter_kwargs': {"icon_css_class": "trio-icon",
                                    "display_column": "name",
                                    "url_name": "view_trio"}},
        "name": {"hidden": True},
        "mother__sample__name": {"label": "Mother"},
        "father__sample__name": {"label": "Father"},
        "proband__sample__name": {"label": "Proband"}
    }

    def __init__(self, user):
        super().__init__(user)
        user_grid_config = UserGridConfig.get(user, self.caption)
        queryset = self.model.filter_for_user(user)
        if not user_grid_config.show_group_data:
            queryset = queryset.filter(user=user)
        self.queryset = queryset.values(*self.get_field_names())
        self.extra_config.update({'sortname': "pk",
                                  'sortorder': "desc"})


class GenomicIntervalsListGrid(JqGridUserRowConfig):
    model = GenomicIntervalsCollection
    caption = 'Genomic Intervals'
    fields = ["id", "name", "import_status", "genome_build__name", "user__username"]
    colmodel_overrides = {
        'id': {"hidden": True},
        "name": {'formatter': 'linkFormatter',
                 'formatter_kwargs': {"icon_css_class": "bed-icon",
                                      "url_name": "view_genomic_intervals",
                                      "url_object_column": "id"}},
        "genome_build__name": {"label": "Genome Build"},
        'user__username': {'label': 'Uploaded by'}
    }

    def __init__(self, user):
        super().__init__(user)
        queryset = get_objects_for_user(user, 'snpdb.view_genomicintervalscollection', accept_global_perms=False)
        self.queryset = queryset.order_by("-pk").values(*self.get_field_names())


class CustomColumnsCollectionListGrid(JqGridUserRowConfig):
    model = CustomColumnsCollection
    caption = 'Custom Columns'
    fields = ["id", "name", "user__username", "modified"]
    colmodel_overrides = {
        'id': {"hidden": True},
        "name": {'formatter': 'linkFormatter',
                 'formatter_kwargs': {"url_name": "view_custom_columns",
                                      "url_object_column": "id"}},
        'user__username': {'label': 'User'},
    }

    def __init__(self, user):
        super().__init__(user)

        user_grid_config = UserGridConfig.get(user, self.caption)
        if user_grid_config.show_group_data:
            queryset = self.model.filter_for_user(user)
        else:
            queryset = self.model.objects.filter(Q(user__isnull=True) | Q(user=user))

        queryset = queryset.annotate(num_columns=Count("customcolumn"))
        field_names = self.get_field_names() + ["num_columns"]
        self.queryset = queryset.values(*field_names)

    def get_colmodels(self, *args, **kwargs):
        colmodels = super().get_colmodels(*args, **kwargs)
        extra = {'index': 'num_columns', 'name': 'num_columns', 'label': 'Number of columns', 'sorttype': 'int'}
        colmodels.append(extra)
        return colmodels


class AbstractVariantGrid(JqGridSQL):
    model = Variant

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._count = None

    def column_in_queryset_fields(self, field):
        colmodel = self.get_override(field)
        return colmodel.get("queryset_field", True)

    def get_queryset_field_names(self):
        field_names = []
        for f in super().get_field_names():
            if self.column_in_queryset_fields(f):
                field_names.append(f)

        return field_names

    def get_sql_params_and_columns(self, request):
        queryset = self.get_filtered_queryset(request)

        sidx = request.GET.get('sidx', 'id')
        if self.column_in_queryset_fields(sidx):
            queryset = self.sort_items(request, queryset)

        select_part, from_part, where_part = get_queryset_select_from_where_parts(queryset)

        extra_columns = []
        extra_select = []
        for alias, select in get_variantgrid_extra_alias_and_select_columns(self.user):
            extra_columns.append(alias)
            extra_select.append(f'({select}) as "{alias}"')
        select_part += ",\n" + ",\n".join(extra_select)

        sql = '\n'.join([select_part, from_part, where_part])
        #logging.info(sql)

        column_names = get_queryset_column_names(queryset, extra_columns)

        params = []
        return sql, params, column_names, True

    def get_count(self, request):
        if self._count is None:
            queryset = self.get_filtered_queryset(request)
            self._count = queryset.count()
        return self._count
