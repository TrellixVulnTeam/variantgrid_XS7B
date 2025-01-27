# Generated by Django 3.1.3 on 2021-01-17 23:42
# Can be deleted when squishing migrations - this has already been added to snpdb/0002 initial data

from django.db import migrations


def _create_columns(apps, schema_editor):
    VariantGridColumn = apps.get_model("snpdb", "VariantGridColumn")

    VARIANT_GRID_COLUMN = [
        {'grid_column_name': 'clingen_allele',
         'variant_column': 'variantallele__allele__clingen_allele',
         'annotation_level': 'V',
         'width': None,
         'label': 'ClinGen Canonical Allele ID',
         'description': '<a href="http://reg.clinicalgenome.org/redmine/projects/registry/genboree_registry/landing">ClinGen Allele Registry</a> Globally unique ID for each sequence change (works across genome builds). WARNING: values are NOT always populated - empty values do not mean there is no record',
         'model_field': True,
         'queryset_field': True},
    ]

    for col_data in VARIANT_GRID_COLUMN:
        VariantGridColumn.objects.get_or_create(**col_data)


class Migration(migrations.Migration):

    dependencies = [
        ('snpdb', '0013_vcfallelesource'),
    ]

    operations = [
        migrations.RunPython(_create_columns),
    ]
