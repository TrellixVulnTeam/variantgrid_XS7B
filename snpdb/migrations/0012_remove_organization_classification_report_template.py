# Generated by Django 3.1 on 2021-01-07 05:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('snpdb', '0011_delete_settingsgenomebuild'),
        ('classification', '0013_auto_20210107_1600')
    ]

    operations = [
        migrations.RemoveField(
            model_name='organization',
            name='classification_report_template',
        ),
    ]
