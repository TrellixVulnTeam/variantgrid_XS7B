# Generated by Django 3.2.4 on 2021-12-24 03:38

from django.db import migrations

from library.django_utils import bulk_insert_class_data, add_new_columns_after


def _new_gene_annotation_columns(apps, schema_editor):
    CustomColumn = apps.get_model("snpdb", "CustomColumn")

    NEW_VARIANT_GRID_COLUMNS = [
        {'grid_column_name': 'mondo_terms',
         'variant_column': 'variantannotation__gene__geneannotation__mondo_terms',
         'annotation_level': 'G',
         'width': None,
         'label': 'MONDO terms',
         'description': 'Mondo Disease Ontology terms associated with gene, joined with " | "',
         'model_field': True,
         'queryset_field': True},
        {'grid_column_name': 'gene_disease_supportive_or_below',
         'variant_column': 'variantannotation__gene__geneannotation__gene_disease_supportive_or_below',
         'annotation_level': 'G',
         'width': None,
         'label': 'Gene/Disease Supportive or below',
         'description': 'GenCC gene/disease classifications of Supportive/Limited, joined with " | "',
         'model_field': True,
         'queryset_field': True},
        {'grid_column_name': 'gene_disease_moderate_or_above',
         'variant_column': 'variantannotation__gene__geneannotation__gene_disease_moderate_or_above',
         'annotation_level': 'G',
         'width': None,
         'label': 'Gene/Disease Moderate or above',
         'description': 'GenCC gene/disease classifications >= Moderate, joined with " | "',
         'model_field': True,
         'queryset_field': True},
    ]

    NEW_COLUMN_VCF_INFO = [
        {'info_id': 'MONDO_TERMS', 'column_id': 'mondo_terms', 'number': None, 'type': 'S',
         'description': 'MONDO terms associated with gene'},
        {'info_id': 'GENE_DISEASE_SUPPORTIVE_OR_BELOW', 'column_id': 'gene_disease_supportive_or_below', 'number': None, 'type': 'S',
         'description': 'GenCC gene/disease classifications of Supportive/Limited. Joined with |'},
        {'info_id': 'GENE_DISEASE_MODERATE_OR_ABOVE', 'column_id': 'gene_disease_moderate_or_above', 'number': None, 'type': 'S',
         'description': 'GenCC gene/disease classifications >= Moderate. Joined with |'},
    ]

    bulk_insert_class_data(apps, "snpdb", [("VariantGridColumn", NEW_VARIANT_GRID_COLUMNS)])
    bulk_insert_class_data(apps, "snpdb", [("ColumnVCFInfo", NEW_COLUMN_VCF_INFO)])

    # Add MONDO terms and gene_disease_moderate_or_above after OMIM/HPO terms
    new_columns = ['mondo_terms', 'gene_disease_moderate_or_above']
    exisitng_with_hpo = CustomColumn.objects.filter(column='hpo_terms')
    add_new_columns_after(exisitng_with_hpo, new_columns)


class Migration(migrations.Migration):

    dependencies = [
        ('annotation', '0040_one_off_add_gene_annotation_columns'),
        ('snpdb', '0056_one_off_upgrade_cyvcf2'),
    ]

    operations = [
        migrations.RunPython(_new_gene_annotation_columns)
    ]
