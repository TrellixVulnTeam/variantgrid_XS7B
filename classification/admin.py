# -*- coding: utf-8 -*-
from django.contrib import admin
from classification.clinvar_export_admin import *  # just done to ensure the file is loaded

from classification.models import ConditionText, ConditionTextMatch, ClinVarExport, ClinVarExportBatch, \
    ClinVarAllele
from classification.models import EvidenceKey, ClassificationReportTemplate
from classification.models.admin_forms import ClinicalContextAdmin, DiscordanceReportAdmin, ConditionTextMatchAdmin, \
    EvidenceKeyAdmin, ConditionTextAdmin, ClassificationReportTemplateAdmin, ClassificationAdmin
from classification.models.classification import Classification
from classification.models.clinical_context_models import ClinicalContext
from classification.models.discordance_models import DiscordanceReportClassification, DiscordanceReport
from snpdb.admin import ModelAdminBasics

# Register your models here.

admin.site.register(EvidenceKey, EvidenceKeyAdmin)
admin.site.register(Classification, ClassificationAdmin)
admin.site.register(ConditionText, ConditionTextAdmin)
admin.site.register(ConditionTextMatch, ConditionTextMatchAdmin)
admin.site.register(ClinicalContext, ClinicalContextAdmin)
admin.site.register(DiscordanceReport, DiscordanceReportAdmin)
admin.site.register(ClassificationReportTemplate, ClassificationReportTemplateAdmin)
# FIXME add all the new ClinVarExport models