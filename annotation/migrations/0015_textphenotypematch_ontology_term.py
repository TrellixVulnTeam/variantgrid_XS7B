# Generated by Django 3.1.3 on 2021-01-21 06:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ontology', '0006_auto_20210121_1026'),
        ('annotation', '0014_auto_20210121_1214'),
    ]

    operations = [
        migrations.AddField(
            model_name='textphenotypematch',
            name='ontology_term',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='ontology.ontologyterm'),
        ),
    ]
