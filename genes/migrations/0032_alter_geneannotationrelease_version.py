# Generated by Django 3.2.1 on 2021-05-19 02:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('genes', '0031_one_off_gene_symbol_alias'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geneannotationrelease',
            name='version',
            field=models.TextField(),
        ),
    ]