# Generated by Django 3.1.3 on 2021-03-30 01:20

from django.db import migrations
from django.db.models import Value, F


def _one_off_gene_coverage_model_changes(apps, schema_editor):
    GeneCoverage = apps.get_model("genes", "GeneCoverage")
    GeneCoverageCanonicalTranscript = apps.get_model("genes", "GeneCoverageCanonicalTranscript")

    GeneCoverage.objects.all().update(percent_1x=Value(100.0) - F("percent_0x"))
    GeneCoverageCanonicalTranscript.objects.all().update(percent_1x=Value(100.0) - F("percent_0x"))


class Migration(migrations.Migration):

    dependencies = [
        ('genes', '0023_auto_20210330_1149'),
    ]

    operations = [
        migrations.RunPython(_one_off_gene_coverage_model_changes)
    ]
