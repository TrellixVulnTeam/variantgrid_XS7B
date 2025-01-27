# Generated by Django 3.2.1 on 2021-07-29 04:57

from django.db import migrations


def _one_off_vcf_reload_af_percent(apps, schema_editor):
    VCF = apps.get_model("snpdb", "VCF")
    PERCENT_AF_VERSION = 14
    legacy_reloaded_vcf_qs = VCF.objects.filter(allele_frequency_percent=True,
                                                uploadedvcf__vcf_importer__version__gte=PERCENT_AF_VERSION)
    legacy_reloaded_vcf_qs.update(allele_frequency_percent=False)


class Migration(migrations.Migration):

    dependencies = [
        ('snpdb', '0039_clinvarkey_behalf_org_id'),
    ]

    operations = [
        migrations.RunPython(_one_off_vcf_reload_af_percent)
    ]
