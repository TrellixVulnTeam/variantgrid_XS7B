# Generated by Django 4.0.4 on 2022-06-23 01:49
from typing import List
from django.db import migrations

"""
This script will allow us to determine which "bucket" a clinical significance value is in.
The numerical value isn't important, just the fact that the values are different.
"""

def populate_buckets(apps, schema_editor):
    log: List[str] = list()
    EvidenceKey = apps.get_model("classification", "EvidenceKey")
    buckets = {
        'B': 1,
        'LB': 1,
        'VUS': 2,
        'VUS_A': 2,
        'VUS_B': 2,
        'VUS_C': 2,
        'LP': 3,
        'P': 3,
        'R': 4,
        'A': None,
        'D': None
    }
    clin_sig = EvidenceKey.objects.get(pk='clinical_significance')
    options = clin_sig.options
    for option in options:
        if key := option.get('key'):
            if key in buckets:
                bucket_value = buckets.get(key)
                option['bucket'] = bucket_value
            else:
                print(f"WARNING: No bucket for Clinical Significance - {key}")
    clin_sig.save()


class Migration(migrations.Migration):

    dependencies = [
        ('classification', '0075_add_new_pathogenicity_prediction_ekeys'),
    ]

    operations = [
        migrations.RunPython(populate_buckets)
    ]
