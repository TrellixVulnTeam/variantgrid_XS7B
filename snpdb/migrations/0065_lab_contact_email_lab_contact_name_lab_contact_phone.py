# Generated by Django 4.0.2 on 2022-03-24 05:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('snpdb', '0064_one_off_common_filter_gnomad_version'),
    ]

    operations = [
        migrations.AddField(
            model_name='lab',
            name='contact_email',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='lab',
            name='contact_name',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='lab',
            name='contact_phone',
            field=models.TextField(blank=True),
        ),
    ]
