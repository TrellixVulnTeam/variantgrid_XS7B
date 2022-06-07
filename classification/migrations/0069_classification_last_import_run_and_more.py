# Generated by Django 4.0.2 on 2022-04-19 06:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classification', '0068_classificationimportrun_logging_version_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='classification',
            name='last_import_run',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='classification.classificationimportrun'),
        ),
        migrations.AddField(
            model_name='classification',
            name='last_source_id',
            field=models.TextField(blank=True, null=True),
        ),
    ]
