# Generated by Django 3.2.6 on 2021-11-22 03:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('snpdb', '0050_change_all_columns'),
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('name', models.TextField(primary_key=True, serialize=False)),
                ('short_name', models.TextField(unique=True, null=True)),
                ('population', models.IntegerField(null=True)),
            ],
        ),
        migrations.RenameField(
            model_name='lab',
            old_name='country',
            new_name='old_country',
        ),
        migrations.RenameField(
            model_name='lab',
            old_name='state',
            new_name='old_state',
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('name', models.TextField(primary_key=True, serialize=False)),
                ('short_name', models.TextField(unique=True, null=True)),
                ('population', models.IntegerField(null=True)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snpdb.country')),
            ],
        ),
    ]