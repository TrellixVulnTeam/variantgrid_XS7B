# Generated by Django 3.2.6 on 2021-11-29 02:07

from django.db import migrations


def _set_alleles(apps, schema_editor):
    """ This can be deleted if there is a blat_keys migration after it """
    Classification = apps.get_model("classification", "Classification")
    VariantAllele = apps.get_model("snpdb", "VariantAllele")

    print("Loading variant alleles")
    va_qs = VariantAllele.objects.filter(variant__varianttag__isnull=False)
    allele_by_variant = dict(va_qs.values_list("variant_id", "allele_id"))

    print("About to assign alleles to all classifications with variants")
    classifications = []
    for (count, c) in enumerate(Classification.objects.filter(allele__isnull=True, variant__isnull=False)):
        if allele_id := allele_by_variant.get(c.variant_id):
            c.allele_id = allele_id
            classifications.append(c)
        if count % 1000 == 0:
            print(f"Processed {count} classifications")

    if classifications:
        print("Performing bulk update")
        Classification.objects.bulk_update(classifications, fields=["allele_id"], batch_size=2000)

    print("Done")


class Migration(migrations.Migration):

    dependencies = [
        ('classification', '0059_classification_allele'),
    ]

    operations = [
        migrations.RunPython(_set_alleles)
    ]
