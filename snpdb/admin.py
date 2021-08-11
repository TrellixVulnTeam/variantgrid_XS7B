from typing import List

from django.contrib import admin, messages
from django.utils.html import format_html
from snpdb import models
from snpdb.admin_utils import AdminExportCsvMixin, ModelAdminBasics, GuardedModelAdminBasics
from snpdb.liftover import liftover_alleles
from snpdb.models import Allele, VariantAllele
from snpdb.models.models_genome import GenomeBuild
from snpdb.models_admin_forms import LabAdmin, OrganizationAdmin


class AlleleClingenFilter(admin.SimpleListFilter):
    title = 'Clingen Filter'
    parameter_name = 'clin'
    default_value = None

    def lookups(self, request, model_admin):
        return [("present", "present"), ("missing", "missing")]

    def queryset(self, request, queryset):
        if value := self.value():
            if value == "present":
                return queryset.filter(clingen_allele__isnull=False)
            if value == "missing":
                return queryset.filter(clingen_allele__isnull=True)
        return queryset


class AlleleAdmin(admin.ModelAdmin, AdminExportCsvMixin):

    list_display = ('pk', 'url', 'clingen_allele', 'variants')
    list_filter = (AlleleClingenFilter,)

    def url(self, obj: Allele):
        return format_html("<a href='{url}'>{url}</a>", url=obj.get_absolute_url())

    def variants(self, obj: Allele):
        genome_builds: List[GenomeBuild] = list()
        for va in VariantAllele.objects.filter(allele=obj).order_by('genome_build'):
            genome_builds.append(va.genome_build)
        if genome_builds:
            return ", ".join(str(genome_build) for genome_build in genome_builds)
        return "-"

    def validate(self, request, queryset):
        allele: Allele
        for allele in queryset:
            allele.validate()

    validate.short_description = 'Validate'

    def liftover(self, request, queryset):
        liftover_alleles(allele_qs=queryset, user=request.user)
        self.message_user(request, message='Liftover queued', level=messages.INFO)

    liftover.short_description = 'Liftover'

    def prepare_clinvar(self, request, queryset):

        from classification.models.clinvar_export_prepare import ClinvarAlleleExportPrepare
        allele: Allele
        for allele in queryset:
            export_prepare = ClinvarAlleleExportPrepare(allele=allele)
            report = export_prepare.update_export_records()
            for message in report:
                self.message_user(request, message=f"Allele ({allele}) - {message}", level=messages.INFO)

    prepare_clinvar.short_description = 'ClinVar Export Prepare'

    actions = ["export_as_csv", validate, liftover, prepare_clinvar]
    search_fields = ('id', 'clingen_allele__id')
    # flag collection and clingen allele blow up as drop downs as there's so many choices in them
    fieldsets = (
        ('No Fields', {'fields': ()}),
    )


class DefaultBuildFilter(admin.SimpleListFilter):
    title = 'Default Genome Build Filter'
    parameter_name = 'default_genome_build'
    default_value = None

    def lookups(self, request, model_admin):
        return [(gb.name, gb.name) for gb in GenomeBuild.objects.filter(enabled=True).order_by('name')]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(default_genome_build=self.value())
        return queryset


class UserSettingsOverrideAdmin(admin.ModelAdmin, AdminExportCsvMixin):
    list_display = ('user', 'default_lab', 'default_genome_build', 'email_weekly_updates', 'email_discordance_updates')
    list_filter = (DefaultBuildFilter,)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    actions = ["export_as_csv"]


class UserPageAck(ModelAdminBasics):
    list_display = ('user', 'page_id')


class ClinVarKeyAdmin(ModelAdminBasics):
    list_display = ('id', 'created', 'modified')

    def get_form(self, request, obj=None, **kwargs):

        return super(ClinVarKeyAdmin, self).get_form(request, obj, widgets={
            'id': admin.widgets.AdminTextInputWidget(),
            'behalf_org_id': admin.widgets.AdminTextInputWidget()
        }, **kwargs)


admin.site.register(models.Allele, AlleleAdmin)
admin.site.register(models.CachedGeneratedFile, ModelAdminBasics)
admin.site.register(models.ClinVarKey, ClinVarKeyAdmin)
admin.site.register(models.Cohort, ModelAdminBasics)
admin.site.register(models.CohortGenotypeCollection, ModelAdminBasics)
admin.site.register(models.CohortSample, ModelAdminBasics)
admin.site.register(models.CustomColumn, ModelAdminBasics)
admin.site.register(models.CustomColumnsCollection, ModelAdminBasics)
admin.site.register(models.GenomeBuild, ModelAdminBasics)
admin.site.register(models.GenomicIntervalsCollection, ModelAdminBasics)
admin.site.register(models.GlobalSettings, ModelAdminBasics)
admin.site.register(models.Lab, LabAdmin)
admin.site.register(models.LabHead, ModelAdminBasics)
admin.site.register(models.LabProject)
admin.site.register(models.LabUserSettingsOverride, ModelAdminBasics)
admin.site.register(models.Manufacturer)
admin.site.register(models.OrganizationUserSettingsOverride, ModelAdminBasics)
admin.site.register(models.Organization, OrganizationAdmin)
admin.site.register(models.Project, ModelAdminBasics)
admin.site.register(models.Sample, ModelAdminBasics)
admin.site.register(models.SampleLabProject)
admin.site.register(models.SampleTag, ModelAdminBasics)
admin.site.register(models.SettingsInitialGroupPermission, ModelAdminBasics)
admin.site.register(models.SiteMessage, ModelAdminBasics)
admin.site.register(models.Tag, ModelAdminBasics)
admin.site.register(models.Trio, ModelAdminBasics)
admin.site.register(models.UserSettingsOverride, UserSettingsOverrideAdmin)
admin.site.register(models.VCF, GuardedModelAdminBasics)
admin.site.register(models.VCFSourceSettings, ModelAdminBasics)
admin.site.register(models.VCFTag, ModelAdminBasics)
admin.site.register(models.VariantGridColumn, ModelAdminBasics)
admin.site.register(models.UserPageAck, UserPageAck)
