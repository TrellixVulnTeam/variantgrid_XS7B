# Generated by Django 3.2.4 on 2021-11-29 04:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('upload', '0011_one_off_convert_skipped_gvcf_to_standard_vcf_info'),
    ]

    operations = [
        migrations.DeleteModel(
            name='VCFSkippedGVCFNonVarBlocks',
        ),
    ]
