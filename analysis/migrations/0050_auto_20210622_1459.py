# Generated by Django 3.1.3 on 2021-06-22 05:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('snpdb', '0035_merge_20210520_1246'),
        ('analysis', '0049_alter_importedvarianttag_analysis_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='varianttag',
            name='variant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='snpdb.variant'),
        ),
    ]