# Generated by Django 3.1 on 2021-02-03 06:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('genes', '0018_hgnc_uniprot_ids'),
        ('annotation', '0020_auto_20210203_1248'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variantannotation',
            name='uniprot',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='genes.uniprot'),
        ),
    ]
