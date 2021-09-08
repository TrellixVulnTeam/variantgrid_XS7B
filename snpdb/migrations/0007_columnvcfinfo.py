# Generated by Django 3.1 on 2020-11-23 03:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('snpdb', '0006_auto_20201122_1150'),
    ]

    operations = [
        migrations.CreateModel(
            name='ColumnVCFInfo',
            fields=[
                ('info_id', models.TextField(primary_key=True, serialize=False)),
                ('number', models.IntegerField(blank=True, null=True)),
                ('type', models.CharField(choices=[('I', 'Integer'), ('F', 'Float'), ('B', 'Flag'), ('C', 'Character'), ('S', 'String')], max_length=1)),
                ('description', models.TextField(null=True)),
                ('column', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='snpdb.variantgridcolumn')),
            ],
        ),
    ]
