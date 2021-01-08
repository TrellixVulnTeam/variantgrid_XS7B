# Generated by Django 3.1 on 2020-12-01 01:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('genes', '0007_activesamplegenelist_samplegenelist'),
        ('analysis', '0009_analysis_version'),
    ]

    operations = [
        migrations.AddField(
            model_name='genelistnode',
            name='sample_gene_list',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='genes.samplegenelist'),
        ),
        migrations.AddField(
            model_name='samplenode',
            name='sample_gene_list',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='genes.samplegenelist'),
        ),
    ]
