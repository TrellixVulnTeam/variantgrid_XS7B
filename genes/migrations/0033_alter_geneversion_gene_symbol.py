# Generated by Django 3.2.1 on 2021-08-24 11:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('genes', '0032_alter_geneannotationrelease_version'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geneversion',
            name='gene_symbol',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='genes.genesymbol'),
        ),
    ]
