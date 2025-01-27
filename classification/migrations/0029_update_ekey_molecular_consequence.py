# Generated by Django 3.1.6 on 2021-05-27 04:55
from typing import List, Dict

from django.db import migrations


def update_key(apps, schema_editor):
    EvidenceKey = apps.get_model("classification", "EvidenceKey")
    if molecular_consequence := EvidenceKey.objects.get(pk="molecular_consequence"):
        options: List[Dict]
        if options := molecular_consequence.options:
            for option in options:
                if option.get('key') == 'initiator_codon_variant':
                    return
            options.append({
                "so": "SO:0001582",
                "key": "initiator_codon_variant",
                "index": 37,
                "label": "Initiator codon variant"
            })
            options = options.sort(key=lambda x: x.get('label'))
            molecular_consequence.save()


class Migration(migrations.Migration):

    dependencies = [
        ('classification', '0028_historic_allele_freq_fixes'),
    ]

    operations = [
        migrations.RunPython(update_key)
    ]
