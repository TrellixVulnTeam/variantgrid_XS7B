# Generated by Django 3.1 on 2020-11-13 03:41

from django.db import migrations


def new_ekey_pubmed_search_terms(apps, schema_editor):
    EvidenceKey = apps.get_model("classification", "EvidenceKey")

    kwargs = {
        'key': 'pubmed_search_terms', 'mandatory': False, 'max_share_level': 'logged_in_users', 'order': 2,
        'label': 'PubMed Search Terms', 'sub_label': None, 'description': 'PubMed search terms for this variant',
        'examples': [], 'options': [], 'see': None, 'evidence_category': 'L', 'value_type': 'T',
        'default_crit_evaluation': None, 'allow_custom_values': False, 'hide': True, 'immutable': False,
        'copy_consensus': True, 'variantgrid_column_id': None,
    }
    EvidenceKey.objects.create(**kwargs)


class Migration(migrations.Migration):

    dependencies = [
        ('classification', '0007_conditionalias_conditionaliassearchcache'),
    ]

    operations = [
        migrations.RunPython(new_ekey_pubmed_search_terms)
    ]
