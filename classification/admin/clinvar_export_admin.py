import json
import re
from datetime import timedelta

from django.contrib import messages, admin
from django.db.models import QuerySet, TextField, Q
from django.db.models.functions import Length, Cast
from django.http import HttpResponse, HttpRequest
from django.utils import timezone

from classification.models import ClinVarExport, ClinVarExportBatch, ClinVarAllele, ClinVarExportBatchStatus, \
    ClinVarExportRequest, ClinVarExportSubmission
from classification.models.clinvar_export_sync import clinvar_export_sync, ClinVarRequestException
from snpdb.admin_utils import AllValuesChoicesFieldListFilter, ModelAdminBasics, admin_action, admin_list_column


class ClinVarExportSubmissionAdmin(admin.TabularInline):
    model = ClinVarExportSubmission
    fields = ('clinvar_export', 'classification_based_on', 'submission_full', 'submission_version', 'localId', 'localKey', 'status', 'scv', 'response_json')

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class ClinVarClassificationAgeFilter(admin.SimpleListFilter):
    title = 'Classification Age'
    parameter_name = 'classification_age'
    default_value = None

    def lookups(self, request, model_admin):
        return [
            ('30', '30+ days old'),
            ('60', '60+ days old'),
            ('90', '90+ days old')
        ]

    def queryset(self, request, queryset):
        if days_old_str := self.value():
            days_old_int = int(days_old_str)
            cut_off_age = timezone.now() - timedelta(days=days_old_int)
            queryset = queryset.filter(classification_based_on__classification__created__lte=cut_off_age)
        return queryset


class InterpretationSummaryLengthFilter(admin.SimpleListFilter):
    title = 'Interpretation Summary Length'
    parameter_name = 'interpretation_summary_length'
    default_value = None
    SUFFIX_MAP = {
        "=": "",
        "<": "__lt",
        "<=": "__lte",
        ">": "__gt",
        ">=": "__gte"
    }

    def lookups(self, request, models_admin):
        return [
            ('=0', 'Empty'),
            ('<200', '199 or less characters'),
            ('>=200', '200+ characters'),
            ('>=300', '300+ characters')
        ]

    def queryset(self, request, queryset: QuerySet[ClinVarExport]):
        if length_check := self.value():
            if match := re.match("(.*?)([0-9]+)", length_check):
                direction = match.group(1)
                length = int(match.group(2))
                queryset = queryset.annotate(interpretation_summary_length=Length(Cast('classification_based_on__published_evidence__interpretation_summary', output_field=TextField())))
                length_q = Q(**{f"interpretation_summary_length{InterpretationSummaryLengthFilter.SUFFIX_MAP[direction]}": length})
                if (direction == '=' and length == 0) or direction.startswith('<'):
                    length_q = length_q | Q(classification_based_on__published_evidence__interpretation_summary__isnull=True)
                queryset = queryset.filter(length_q)
            else:
                raise ValueError(f"Internal error, can't parse {length_check}")
        return queryset


@admin.register(ClinVarExport)
class ClinVarExportAdmin(ModelAdminBasics):
    list_display = ("pk", "clinvar_allele", "status", "classification_based_on", "classification_created", "condition_smart", "scv", "latest_batch", "created", "modified")
    list_filter = (('clinvar_allele__clinvar_key', admin.RelatedFieldListFilter), ('status', AllValuesChoicesFieldListFilter), ClinVarClassificationAgeFilter, InterpretationSummaryLengthFilter)
    search_fields = ('pk', "scv")
    inlines = (ClinVarExportSubmissionAdmin, )
    list_select_related = ('classification_based_on', )
    list_per_page = 200

    def has_add_permission(self, request, obj=None):
        return False

    def get_form(self, request, obj=None, **kwargs):
        return super().get_form(request, obj, widgets={
            'scv': admin.widgets.AdminTextInputWidget()
        }, **kwargs)

    @admin_list_column(short_description="Classification Created", order_field="classification_based_on__classification__created")
    def classification_created(self, obj: ClinVarExport):
        if cm := obj.classification_based_on:
            return f"{(timezone.now() - cm.classification.created).days} days old : {cm.classification.created.strftime('%Y-%m-%d')}"
            # return cm.classification.created.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    @admin_list_column(short_description="Condition",
                       order_field="condition__sort_text")
    def condition_smart(self, obj: ClinVarExport):
        condition = obj.condition
        if display_text := condition.get('display_text'):
            return display_text
        return condition

    @admin_list_column("Latest Batch")
    def latest_batch(self, obj: ClinVarExport):
        if submission := obj.clinvarexportsubmission_set.order_by('-pk').first():
            return submission.submission_batch_id

    @admin_action("Add to ClinVar Submission Batch")
    def add_to_batch(self, request, queryset):
        batches = ClinVarExportBatch.create_batches(queryset, force_update=True)
        if batches:
            for batch in batches:
                messages.info(request, message=f"Submission Batch for {batch.clinvar_key} created with {batch.clinvarexportsubmission_set.count()} submissions")
        else:
            messages.warning(request, message="No records in pending non-errored state to add to a new batch")

    @admin_action("Re-calculate status")
    def force_recalc_status(self, request, queryset: QuerySet[ClinVarExport]):
        for export in queryset:
            export.update()


@admin.register(ClinVarAllele)
class ClinVarAlleleAdmin(ModelAdminBasics):
    list_display = ("pk", "clinvar_key", "allele", "classifications_missing_condition", "submissions_valid", "submissions_invalid", "last_evaluated")
    search_fields = ("pk", "allele__pk")
    list_filter = (('clinvar_key', admin.RelatedFieldListFilter), )

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ClinVarExportRequestAdmin(admin.TabularInline):
    model = ClinVarExportRequest

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(ClinVarExportBatch)
class ClinVarExportBatchAdmin(ModelAdminBasics):
    list_display = ("pk", "clinvar_key", "created", "modified", "record_count", "status")
    list_filter = (('status', AllValuesChoicesFieldListFilter), ('clinvar_key', admin.RelatedFieldListFilter))
    search_fields = ('pk', )
    inlines = (ClinVarExportRequestAdmin, ClinVarExportSubmissionAdmin)

    def has_add_permission(self, request, obj=None):
        return False

    def get_form(self, request, obj=None, **kwargs):
        return super().get_form(request, obj, widgets={
            'submission_identifier': admin.widgets.AdminTextInputWidget(),
            'file_url': admin.widgets.AdminURLFieldWidget()
        }, **kwargs)

    @admin_list_column(short_description="Record Count")
    def record_count(self, obj: ClinVarExportBatch):
        return obj.clinvarexportsubmission_set.count()

    @admin_action("Reject")
    def reject(self, request: HttpRequest, queryset: QuerySet[ClinVarExportBatch]):
        for ceb in queryset:
            ceb.reject()

    @admin_action("Regenerate")
    def regenerate(self, request: HttpRequest, queryset: QuerySet[ClinVarExportBatch]):
        for ceb in queryset:
            ceb.regenerate()

    @admin_action("Download JSON")
    def download_json(self, request, queryset: QuerySet[ClinVarExportBatch]):
        if queryset.count() != 1:
            messages.error(request, message="Error Can only download one batch at a time")
            return

        batch: ClinVarExportBatch = queryset.first()

        batch_json = batch.to_json()
        batch_json_str = json.dumps(batch_json)

        response = HttpResponse(batch_json_str, content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename=clinvar_export_preview_{batch.pk}.json'
        return response

    @admin_action("Next Action")
    def next_action(self, request, queryset: QuerySet[ClinVarExportBatch]):
        queryset: QuerySet[ClinVarExportBatch] = queryset.filter(status__in=(
            ClinVarExportBatchStatus.UPLOADING,
            ClinVarExportBatchStatus.AWAITING_UPLOAD
        ))
        if not queryset:
            messages.error(request, message="No selected records in status of Uploading or Awaiting Upload")
        else:
            for batch in queryset:
                try:
                    clinvar_export_sync.next_request(batch)
                    messages.success(request, message=f"Batch {batch.pk} - updated")
                except ClinVarRequestException as clinvar_except:
                    messages.error(request, message=f"Batch {batch.pk} - {clinvar_except}")
