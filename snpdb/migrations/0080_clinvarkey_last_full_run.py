# Generated by Django 4.0.4 on 2022-08-02 04:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('snpdb', '0079_rename_conversion_tool_allelemergelog_allele_linking_tool_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='clinvarkey',
            name='last_full_run',
            field=models.DateTimeField(null=True),
        ),
    ]
