# Generated by Django 3.1 on 2021-01-12 02:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ontology', '0003_ontologyimport_completed'),
    ]

    operations = [
        migrations.AddField(
            model_name='ontologytermgenerelation',
            name='deletion_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
