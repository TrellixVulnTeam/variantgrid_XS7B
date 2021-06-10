# Generated by Django 3.1.6 on 2021-06-09 05:16

from django.db import migrations

def _insert_variant_panel_frequency_key(apps, schema_editor):
    """ This can be deleted if there is a blat_keys migration after it """
    EvidenceKey = apps.get_model("classification", "EvidenceKey")
    EvidenceKey.objects.create(
        key="variant_panel_frequency",
        evidence_category="HT",
        hide=True,
        order=7,
        value_type="F",
        copy_consensus=False
    )


class Migration(migrations.Migration):

    dependencies = [
        ('classification', '0031_remove_clinvarexport_gene_symbol'),
    ]

    operations = [
        migrations.RunPython(_insert_variant_panel_frequency_key)
    ]
