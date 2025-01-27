# Generated by Django 4.0.3 on 2022-04-22 07:12
import logging

from django.db import migrations


def _one_off_link_hgnc_and_uniprot(apps, schema_editor):
    HGNC = apps.get_model("genes", "HGNC")
    UniProt = apps.get_model("genes", "UniProt")

    # We only store uni prot IDs that have info we care about, so not all will link
    uniprot_pks = set(UniProt.objects.all().values_list("pk", flat=True))
    if not uniprot_pks:
        return

    hgnc_records = []
    for hgnc in HGNC.objects.filter(uniprot__isnull=True, uniprot_ids__isnull=False).exclude(uniprot_ids=''):
        for up_id in hgnc.uniprot_ids.split(","):
            if up_id in uniprot_pks:
                hgnc.uniprot_id = up_id
                hgnc_records.append(hgnc)

    if hgnc_records:
        logging.info("Linking %d HGNC w/uniprot", len(hgnc_records))
        HGNC.objects.bulk_update(hgnc_records, fields=["uniprot_id"], batch_size=2000)


class Migration(migrations.Migration):

    dependencies = [
        ('genes', '0055_hgnc_uniprot'),
    ]

    operations = [
        migrations.RunPython(_one_off_link_hgnc_and_uniprot),
    ]
