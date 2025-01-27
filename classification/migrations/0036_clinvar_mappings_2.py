# Generated by Django 3.1.6 on 2021-07-16 06:41

from django.db import migrations

from classification.autopopulate_evidence_keys.clinvar_option_updator import ClinVarOptionUpdator


def affected_status(apps, schema_editor):
    options = ClinVarOptionUpdator(apps, "affected_status")
    options.set_clinvar_option("yes", "yes")
    options.set_clinvar_option("no", "no")
    options.set_clinvar_option("unknown", "unknown")
    options.set_clinvar_option("not_applicable", "not applicable")

class Migration(migrations.Migration):

    dependencies = [
        ('classification', '0035_auto_20210709_1358'),
    ]

    operations = [
        migrations.RunPython(affected_status)
    ]
