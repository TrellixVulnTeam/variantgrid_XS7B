# Generated by Django 3.1 on 2021-02-16 03:35

from django.db import migrations

from library.django_utils import bulk_insert_class_data


def _new_columns_gnomad3(apps, schema_editor):
    NEW_VARIANT_GRID_COLUMNS = [
        {'grid_column_name': 'gnomad_ac',
         'variant_column': 'variantannotation__gnomad_ac',
         'annotation_level': 'V',
         'width': None,
         'label': 'gnomAD AC',
         'description': "gnomAD: Alternate Allele Count  (GRCh38 only)",
         'model_field': True,
         'queryset_field': True},
        {'grid_column_name': 'gnomad_an',
         'variant_column': 'variantannotation__gnomad_an',
         'annotation_level': 'V',
         'width': None,
         'label': 'gnomAD AC',
         'description': "gnomAD: Total number of alleles  (GRCh38 only)",
         'model_field': True,
         'queryset_field': True},
        {'grid_column_name': 'gnomad_popmax_ac',
         'variant_column': 'variantannotation__gnomad_popmax_ac',
         'annotation_level': 'V',
         'width': None,
         'label': 'gnomAD AC',
         'description': "gnomAD: Allele count in the population with the maximum AF  (GRCh38 only)",
         'model_field': True,
         'queryset_field': True},
        {'grid_column_name': 'gnomad_popmax_an',
         'variant_column': 'variantannotation__gnomad_popmax_an',
         'annotation_level': 'V',
         'width': None,
         'label': 'gnomAD AC',
         'description': "gnomAD: Total number of alleles in the population with the maximum AF  (GRCh38 only)",
         'model_field': True,
         'queryset_field': True},
        {'grid_column_name': 'gnomad_popmax_hom_alt',
         'variant_column': 'variantannotation__gnomad_popmax_hom_alt',
         'annotation_level': 'V',
         'width': None,
         'label': 'gnomAD AC',
         'description': "gnomAD: Count of homozygous individuals in the population with the maximum allele frequency (GRCh38 only)",
         'model_field': True,
         'queryset_field': True},
        {'grid_column_name': 'gnomad2_liftover_af',
         'variant_column': 'variantannotation__gnomad2_liftover_af',
         'annotation_level': 'V',
         'width': None,
         'label': 'gnomAD2 AF',
         'description': "gnomAD2: Allele Frequency from gnomAD2 liftover (GRCh38 only)",
         'model_field': True,
         'queryset_field': True},
    ]

    NEW_COLUMN_VCF_INFO = [
        {'info_id': 'GNOMAD3_AC',
         'column_id': 'gnomad_ac',
         'number': None,
         'type': 'F',
         'description': "gnomAD: Alternate Allele Count  (GRCh38 only)"},
        {'info_id': 'GNOMAD3_AN',
         'column_id': 'gnomad_an',
         'number': None,
         'type': 'I',
         'description': "gnomAD: Total number of alleles  (GRCh38 only)"},
        {'info_id': 'GNOMAD3_POPMAX_AC',
         'column_id': 'gnomad_popmax_ac',
         'number': None,
         'type': 'I',
         'description': "gnomAD: Allele count in the population with the maximum AF  (GRCh38 only)"},
        {'info_id': 'GNOMAD3_POPMAX_AN',
         'column_id': 'gnomad_popmax_an',
         'number': None,
         'type': 'I',
         'description': "gnomAD: Total number of alleles in the population with the maximum AF  (GRCh38 only)"},
        {'info_id': 'GNOMAD3_POPMAX_HOM_ALT',
         'column_id': 'gnomad_popmax_hom_alt',
         'number': None,
         'type': 'I',
         'description': "gnomAD: Count of homozygous individuals in the population with the maximum allele frequency (GRCh38 only)"},
        {'info_id': 'GNOMAD2_LIFTOVER_AF',
         'column_id': 'gnomad2_liftover_af',
         'number': None,
         'type': 'F',
         'description': "gnomAD: Allele Frequency from gnomAD2 liftover (GRCh38 only)"},
    ]

    bulk_insert_class_data(apps, "snpdb", [("VariantGridColumn", NEW_VARIANT_GRID_COLUMNS)])
    bulk_insert_class_data(apps, "snpdb", [("ColumnVCFInfo", NEW_COLUMN_VCF_INFO)])


class Migration(migrations.Migration):

    dependencies = [
        ('snpdb', '0018_variantallelecollectionrecord_variantallelecollectionsource'),
    ]

    operations = [
        migrations.RunPython(_new_columns_gnomad3)
    ]
