# Generated by Django 4.0.3 on 2022-03-15 05:28

from django.db import migrations


def _one_off_common_filter_gnomad_version(apps, schema_editor):
    """ This is done to match annotation.0042_one_off_variant_annotation_version_gnomad """
    CohortGenotypeCommonFilterVersion = apps.get_model("snpdb", "CohortGenotypeCommonFilterVersion")
    # We do our own custom VEP annotation with gnomAD, use that for versions now, update historical ones
    vav_qs = CohortGenotypeCommonFilterVersion.objects.filter(gnomad_version='r2.1')
    vav_qs.filter(genome_build='GRCh37').update(gnomad_version='2.1.1')
    vav_qs.filter(genome_build='GRCh38').update(gnomad_version='3.1')


class Migration(migrations.Migration):

    dependencies = [
        ('snpdb', '0063_auto_20220307_1341'),
    ]

    operations = [
        migrations.RunPython(_one_off_common_filter_gnomad_version)
    ]
