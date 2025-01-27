# Generated by Django 3.2.4 on 2022-02-08 03:01

from django.db import migrations


def _one_off_set_variant_tag_allele(apps, schema_editor):
    VariantAllele = apps.get_model("snpdb", "VariantAllele")
    VariantTag = apps.get_model("analysis", "VariantTag")

    print("About to assign alleles to all variant tags")

    # don't want to trigger update date for changing this
    variant_tags = []
    num_missing_alleles = 0

    print("Loading variant alleles")
    va_qs = VariantAllele.objects.filter(variant__varianttag__isnull=False)
    allele_by_variant = dict(va_qs.values_list("variant_id", "allele_id"))

    print("Processing variant tags")
    for count, vt in enumerate(VariantTag.objects.filter(allele__isnull=True)):
        if allele_id := allele_by_variant.get(vt.variant_id):
            vt.allele_id = allele_id
            variant_tags.append(vt)
        else:
            num_missing_alleles += 1

        if count and count % 1000 == 0:
            print(f"Processed {count} variant tags")

    if variant_tags:
        print(f"Performing bulk update on {len(variant_tags)}")
        VariantTag.objects.bulk_update(variant_tags, fields=["allele_id"], batch_size=2000)

    if num_missing_alleles:
        print(f"Warning: {num_missing_alleles} tags missing alleles")

    print("Done")


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0057_varianttag_allele'),
    ]

    operations = [
        migrations.RunPython(_one_off_set_variant_tag_allele)
    ]
