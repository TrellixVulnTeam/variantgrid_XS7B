# Generated by Django 4.0.7 on 2022-10-06 00:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ontology', '0023_alter_ontologyterm_status'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='ontologyversion',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='ontologyversion',
            name='omim_import',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='omim_ontology_version', to='ontology.ontologyimport'),
        ),
        migrations.AlterUniqueTogether(
            name='ontologyversion',
            unique_together={('gencc_import', 'mondo_import', 'hp_owl_import', 'hp_phenotype_to_genes_import', 'omim_import')},
        ),
    ]
