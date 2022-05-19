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
    NMD = "N"
    PATHOGENICITY_PREDICTIONS = 'P'

    COLUMN_VEP_FIELD = [
        {'column': 'nmd_escaping_variant', 'vep_plugin': NMD, 'variant_grid_column_id': 'nmd_escaping_variant',
         'source_field': 'NMD', 'category': PATHOGENICITY_PREDICTIONS, 'min_vep_columns_version': 2},
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
        # ALoFT
        {'column': 'aloft_prob_tolerant', 'vep_plugin': DBNSFP, 'variant_grid_column_id': 'aloft_prob_tolerant',
         'source_field': 'Aloft_prob_Tolerant', 'category': PATHOGENICITY_PREDICTIONS, 'min_vep_columns_version': 2},
        {'column': 'aloft_prob_recessive', 'vep_plugin': DBNSFP, 'variant_grid_column_id': 'aloft_prob_recessive',
         'source_field': 'Aloft_prob_Recessive', 'category': PATHOGENICITY_PREDICTIONS, 'min_vep_columns_version': 2},
        {'column': 'aloft_prob_dominant', 'vep_plugin': DBNSFP, 'variant_grid_column_id': 'aloft_prob_dominant',
         'source_field': 'Aloft_prob_Dominant', 'category': PATHOGENICITY_PREDICTIONS, 'min_vep_columns_version': 2},
        {'column': 'aloft_pred', 'vep_plugin': DBNSFP, 'variant_grid_column_id': 'aloft_pred',
         'source_field': 'Aloft_pred', 'category': PATHOGENICITY_PREDICTIONS, 'min_vep_columns_version': 2},
        {'column': 'aloft_high_confidence', 'vep_plugin': DBNSFP, 'variant_grid_column_id': 'aloft_high_confidence',
         'source_field': 'Aloft_Confidence', 'category': PATHOGENICITY_PREDICTIONS, 'min_vep_columns_version': 2},
    ]

    bulk_insert_class_data(apps, "annotation", [("ColumnVEPField", COLUMN_VEP_FIELD)])


def _reverse_new_vep_column_version(apps, schema_editor):
    ColumnVEPField = apps.get_model("annotation", "ColumnVEPField")
    NEW_COLUMNS = ['nmd_escaping_variant', 'cadd_raw_rankscore', 'revel_rankscore', 'bayesdel_noaf_rankscore',
                   'clinpred_rankscore', 'vest4_rankscore', 'metalr_rankscore', 'aloft_prob_tolerant',
                   'aloft_prob_recessive', 'aloft_prob_dominant', 'aloft_pred', 'aloft_high_confidence']

    ColumnVEPField.objects.filter(column__in=NEW_COLUMNS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('annotation', '0052_columnvepfield_max_vep_columns_version_and_more'),
        ('snpdb', '0073_new_vep_columns'),
    ]

    operations = [
        migrations.RunPython(_new_vep_column_version, reverse_code=_reverse_new_vep_column_version),
    ]
