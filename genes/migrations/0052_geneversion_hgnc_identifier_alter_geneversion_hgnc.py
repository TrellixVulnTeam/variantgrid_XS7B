# Generated by Django 4.0.3 on 2022-03-22 03:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('genes', '0051_alter_transcriptversion_contig'),
    ]

    operations = [
        migrations.AddField(
            model_name='geneversion',
            name='hgnc_identifier',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='geneversion',
            name='hgnc',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='genes.hgnc'),
        ),
    ]
