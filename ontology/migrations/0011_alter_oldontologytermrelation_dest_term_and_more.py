# Generated by Django 4.0.2 on 2022-06-17 07:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ontology', '0010_rename_ontologytermrelation_oldontologytermrelation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oldontologytermrelation',
            name='dest_term',
            field=models.ForeignKey(db_index=False, on_delete=django.db.models.deletion.CASCADE, to='ontology.ontologyterm'),
        ),
        migrations.AlterField(
            model_name='oldontologytermrelation',
            name='from_import',
            field=models.ForeignKey(db_index=False, on_delete=django.db.models.deletion.PROTECT, to='ontology.ontologyimport'),
        ),
        migrations.AlterField(
            model_name='oldontologytermrelation',
            name='source_term',
            field=models.ForeignKey(db_index=False, on_delete=django.db.models.deletion.CASCADE, related_name='subject', to='ontology.ontologyterm'),
        ),
    ]
