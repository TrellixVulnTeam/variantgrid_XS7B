# Generated by Django 3.1.3 on 2021-02-25 04:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('genes', '0021_delete_rvis'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gene',
            name='summary',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='hgnc',
            name='ccds_ids',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='hgnc',
            name='ensembl_gene_id',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='hgnc',
            name='gene_group_ids',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='hgnc',
            name='gene_groups',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='hgnc',
            name='location',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='hgnc',
            name='mgd_ids',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='hgnc',
            name='omim_ids',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='hgnc',
            name='previous_symbols',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='hgnc',
            name='refseq_ids',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='hgnc',
            name='rgd_ids',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='hgnc',
            name='ucsc_ids',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='hgnc',
            name='uniprot_ids',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='uniprot',
            name='function',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='uniprot',
            name='pathway',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='uniprot',
            name='pathway_interaction_db',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='uniprot',
            name='reactome',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='uniprot',
            name='tissue_specificity',
            field=models.TextField(blank=True, null=True),
        ),
    ]
