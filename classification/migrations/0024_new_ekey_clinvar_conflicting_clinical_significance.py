# Generated by Django 3.1.3 on 2021-03-04 00:44

from django.db import migrations


def _new_ekey_clinvar_conflicting_clinical_significance(apps, schema_editor):
    EvidenceKey = apps.get_model("classification", "EvidenceKey")

    kwargs = {
        'key': 'clinvar_conflicting_clinical_significance', 'mandatory': False, 'max_share_level': 'logged_in_users',
        'order': 10,
        'label': 'ClinVar Conflicting Clinical Significance', 'sub_label': '',
        'description': "Conflicting clinical significance for this single variant",
        'examples': ['Likely_pathogenic(1),Uncertain_significance(1)'], 'options': [], 'see': 'https://www.ncbi.nlm.nih.gov/clinvar/',
        'evidence_category': 'DB', 'value_type': 'F', 'default_crit_evaluation': None,
        'allow_custom_values': False, 'hide': False, 'immutable': False, 'copy_consensus': False,
        'variantgrid_column_id': 'conflicting_clinical_significance'
    }
    EvidenceKey.objects.create(**kwargs)


class Migration(migrations.Migration):

    dependencies = [
        ('classification', '0023_merge_20210218_1401'),
        ('snpdb', '0022_new_column_clinvar_conflicting_clinical_significance'),
    ]

    operations = [
        migrations.RunPython(_new_ekey_clinvar_conflicting_clinical_significance)
    ]
