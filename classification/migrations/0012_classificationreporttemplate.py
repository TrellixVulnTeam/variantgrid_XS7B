# Generated by Django 3.1 on 2021-01-07 05:29

import django.utils.timezone
import model_utils.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classification', '0011_auto_20210106_1016'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassificationReportTemplate',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.TextField(primary_key=True, serialize=False)),
                ('template', models.TextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
