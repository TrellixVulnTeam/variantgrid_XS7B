# Generated by Django 3.2.1 on 2021-05-10 00:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0039_remove_genelistnode_has_gene_coverage'),
    ]

    operations = [
        migrations.AddField(
            model_name='genelistnode',
            name='has_gene_coverage',
            field=models.BooleanField(null=True),
        ),
    ]