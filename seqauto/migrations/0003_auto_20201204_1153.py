# Generated by Django 3.1 on 2020-12-04 01:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('genes', '0007_activesamplegenelist_samplegenelist'),
        ('seqauto', '0002_initial_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='bamfile',
            name='file_last_modified',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='fastq',
            name='file_last_modified',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='fastqc',
            name='file_last_modified',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='flagstats',
            name='file_last_modified',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='illuminaflowcellqc',
            name='file_last_modified',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='qc',
            name='file_last_modified',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='qcexecsummary',
            name='file_last_modified',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='qcgenecoverage',
            name='file_last_modified',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='qcgenelist',
            name='file_last_modified',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='qcgenelist',
            name='sample_gene_list',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='genes.samplegenelist'),
        ),
        migrations.AddField(
            model_name='samplesheetcombinedvcffile',
            name='file_last_modified',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='vcffile',
            name='file_last_modified',
            field=models.FloatField(default=0.0),
        ),
    ]
