from django.contrib import messages, admin
from django.db.models import QuerySet
from django.http import HttpResponse

from classification.models import ClinVarExport, ClinVarExportBatch, ClinVarAllele, ClinVarExportBatchStatus, ClinVarExportRequest
from classification.models.clinvar_export_sync import clinvar_export_sync, ClinVarRequestException
from snpdb.admin_utils import AllValuesChoicesFieldListFilter, ModelAdminBasics, admin_action
import json


@admin.register(ClinVarExport)
class ClinVarExportAdmin(ModelAdminBasics):
    list_display = ("pk", "clinvar_allele", "status", "release_status", "classification_based_on", "condition", "scv", "created", "modified")
    list_filter = (('clinvar_allele__clinvar_key', admin.RelatedFieldListFilter), ('status', AllValuesChoicesFieldListFilter))
    search_fields = ('pk', "scv")

    def has_add_permission(self, request, obj=None):
        return False

    def get_form(self, request, obj=None, **kwargs):
        return super(ClinVarExportAdmin, self).get_form(request, obj, widgets={
            'scv': admin.widgets.AdminTextInputWidget()
        }, **kwargs)

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
    inlines = (ClinVarExportRequestAdmin,)

    def has_add_permission(self, request, obj=None):
        return False

    def get_form(self, request, obj=None, **kwargs):
        return super().get_form(request, obj, widgets={
            'submission_identifier': admin.widgets.AdminTextInputWidget(),
            'file_url': admin.widgets.AdminURLFieldWidget()
        }, **kwargs)

    def record_count(self, obj: ClinVarExportBatch):
        return obj.clinvarexportsubmission_set.count()

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