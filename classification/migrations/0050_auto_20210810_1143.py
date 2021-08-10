# Generated by Django 3.1.6 on 2021-08-10 02:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classification', '0049_auto_20210809_1431'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='clinvarexportbatch',
            options={'verbose_name': 'ClinVar Export batch'},
        ),
        migrations.RemoveField(
            model_name='clinvarexport',
            name='processed_json',
        ),
        migrations.AddField(
            model_name='clinvarexportsubmission',
            name='localId',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='clinvarexportsubmission',
            name='localKey',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='clinvarexportsubmission',
            name='scv',
            field=models.TextField(blank=True, null=True),
        ),
    ]
