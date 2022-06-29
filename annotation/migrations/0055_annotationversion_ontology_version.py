# Generated by Django 4.0.2 on 2022-06-20 03:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ontology', '0015_ontologyimport_version_ontologyversion'),
        ('annotation', '0054_one_off_cols_v2_pathogenic_counts'),
    ]

    operations = [
        migrations.AddField(
            model_name='annotationversion',
            name='ontology_version',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='ontology.ontologyversion'),
        ),
    ]
