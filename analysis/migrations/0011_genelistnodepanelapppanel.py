# Generated by Django 3.1.3 on 2021-01-14 05:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('genes', '0010_auto_20210114_1530'),
        ('analysis', '0010_auto_20201201_1152'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeneListNodePanelAppPanel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gene_list_node', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.genelistnode')),
                ('panel_app_panel_local_cache_gene_list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='genes.panelapppanellocalcachegenelist')),
            ],
        ),
    ]
