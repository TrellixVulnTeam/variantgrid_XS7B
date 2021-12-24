# Generated by Django 3.2.4 on 2021-12-24 01:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annotation', '0038_auto_20211223_1532'),
    ]

    operations = [
        migrations.AddField(
            model_name='geneannotation',
            name='gene_disease_moderate_or_above',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='geneannotation',
            name='gene_disease_supportive_or_below',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='geneannotation',
            name='mondo_terms',
            field=models.TextField(null=True),
        ),
    ]
