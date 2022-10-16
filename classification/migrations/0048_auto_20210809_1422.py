# Generated by Django 3.1.6 on 2021-08-09 04:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classification', '0047_auto_20210806_1122'),
    ]

    operations = [
        migrations.AddField(
            model_name='clinvarexport',
            name='processed_json',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='clinvarexportrequest',
            name='handled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='clinvarexportrequest',
            name='url',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='clinvarexportsubmissionbatch',
            name='file_url',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='clinvarexportsubmissionbatch',
            name='submission_identifier',
            field=models.TextField(blank=True, null=True),
        ),
    ]