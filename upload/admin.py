from django.contrib import admin
from django.contrib.auth.models import User

from snpdb.admin_utils import ModelAdminBasics
from snpdb.models import ProcessingStatus
from . import models
from .models import UploadStep


class UploadStepStatusFilter(admin.SimpleListFilter):
    title = 'Status'
    parameter_name = 'status'
    default_value = None

    def lookups(self, request, model_admin):
        return ProcessingStatus.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


class UploadStepAdmin(ModelAdminBasics):
    list_display = ('id', 'name', 'upload_pipeline', 'status', 'start_date', 'end_date', 'error_message')
    list_filter = (UploadStepStatusFilter,)
    search_fields = ('id', 'name')

    def mark_timed_out(self, request, queryset):
        user: User = request.user
        us: UploadStep
        for us in queryset:
            us.mark_timed_out(user=user)

    mark_timed_out.short_description = "Mark process as timed out"

    actions = [mark_timed_out]


admin.site.register(models.UploadedFile)
admin.site.register(models.UploadPipeline)
admin.site.register(models.UploadedVCF)
admin.site.register(models.UploadStep, UploadStepAdmin)
