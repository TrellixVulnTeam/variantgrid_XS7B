# Generated by Django 4.0.3 on 2022-05-16 05:19

from django.db import migrations

from library.django_utils import bulk_insert_class_data


def _new_vep_column_version(apps, schema_editor):
    ColumnVEPField = apps.get_model("annotation", "ColumnVEPField")

    # Any old ones are now version 1
    VERSION_1 = [
        "fathmm_pred_most_damaging",
        "mutation_assessor_pred_most_damaging",
        "mutation_taster_pred_most_damaging",
        "polyphen2_hvar_pred_most_damaging",
        "revel_score",
        "cadd_phred",
    ]
    ColumnVEPField.objects.filter(column__in=VERSION_1).update(max_vep_columns_version=1)

    DBNSFP = 'd'
    LOFTEE = "t"
    NMD = "N"
    PATHOGENICITY_PREDICTIONS = 'P'

    COLUMN_VEP_FIELD = [
        {'column': 'nmd_escaping_variant', 'vep_plugin': NMD, 'variant_grid_column_id': 'nmd_escaping_variant',
         'source_field': 'NMD', 'category': PATHOGENICITY_PREDICTIONS, 'min_vep_columns_version': 2},
        {'column': 'lof', 'vep_plugin': LOFTEE, 'variant_grid_column_id': 'lof',
         'source_field': 'LoF', 'category': PATHOGENICITY_PREDICTIONS, 'min_vep_columns_version': 2},
        {'column': 'lof_filter', 'vep_plugin': LOFTEE, 'variant_grid_column_id': 'lof_filter',
         'source_field': 'LoF_filter', 'category': PATHOGENICITY_PREDICTIONS, 'min_vep_columns_version': 2},
        {'column': 'lof_flags', 'vep_plugin': LOFTEE, 'variant_grid_column_id': 'lof_flags',
         'source_field': 'LoF_flags', 'category': PATHOGENICITY_PREDICTIONS, 'min_vep_columns_version': 2},
        {'column': 'lof_info', 'vep_plugin': LOFTEE, 'variant_grid_column_id': 'lof_info',
         'source_field': 'LoF_info', 'category': PATHOGENICITY_PREDICTIONS, 'min_vep_columns_version': 2},
        {'column': 'cadd_raw_rankscore', 'vep_plugin': DBNSFP, 'variant_grid_column_id': 'cadd_raw_rankscore',
         'source_field': 'CADD_raw_rankscore', 'category': PATHOGENICITY_PREDICTIONS, 'min_vep_columns_version': 2},
        {'column': 'revel_rankscore', 'vep_plugin': DBNSFP, 'variant_grid_column_id': 'revel_rankscore',
         'source_field': 'REVEL_rankscore', 'category': PATHOGENICITY_PREDICTIONS, 'min_vep_columns_version': 2},
        {'column': 'bayesdel_noaf_rankscore', 'vep_plugin': DBNSFP, 'variant_grid_column_id': 'bayesdel_noaf_rankscore',
         'source_field': 'BayesDel_noAF_rankscore', 'category': PATHOGENICITY_PREDICTIONS, 'min_vep_columns_version': 2},
        {'column': 'clinpred_rankscore', 'vep_plugin': DBNSFP, 'variant_grid_column_id': 'clinpred_rankscore',
         'source_field': 'ClinPred_rankscore', 'category': PATHOGENICITY_PREDICTIONS, 'min_vep_columns_version': 2},
        {'column': 'vest4_rankscore', 'vep_plugin': DBNSFP, 'variant_grid_column_id': 'vest4_rankscore',
         'source_field': 'VEST4_rankscore', 'category': PATHOGENICITY_PREDICTIONS, 'min_vep_columns_version': 2},
        {'column': 'metalr_rankscore', 'vep_plugin': DBNSFP, 'variant_grid_column_id': 'metalr_rankscore',
         'source_field': 'MetaLR_rankscore', 'category': PATHOGENICITY_PREDICTIONS, 'min_vep_columns_version': 2},
    ]

    bulk_insert_class_data(apps, "annotation", [("ColumnVEPField", COLUMN_VEP_FIELD)])


class Migration(migrations.Migration):

    dependencies = [
        ('annotation', '0052_columnvepfield_max_vep_columns_version_and_more'),
        ('snpdb', '0073_new_vep_columns'),
    ]

    operations = [
        migrations.RunPython(_new_vep_column_version),
    ]