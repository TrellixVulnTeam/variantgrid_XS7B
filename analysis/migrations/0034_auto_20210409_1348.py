# Generated by Django 3.1.3 on 2021-04-09 04:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('snpdb', '0030_one_off_fix_cohort_sample_order'),
        ('analysis', '0033_one_off_variant_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='varianttag',
            name='genome_build',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snpdb.genomebuild'),
        ),
    ]
