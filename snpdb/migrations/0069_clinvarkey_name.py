# Generated by Django 4.0.4 on 2022-04-28 02:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('snpdb', '0068_update_uniprot_columns'),
    ]

    operations = [
        migrations.AddField(
            model_name='clinvarkey',
            name='name',
            field=models.TextField(blank=True, default=''),
        ),
    ]