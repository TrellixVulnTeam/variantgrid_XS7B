# Generated by Django 4.1 on 2022-08-19 01:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('seqauto', '0031_alter_goldcoveragesummary_transcript_version'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='seqautorun',
            options={'permissions': (('seqauto_scan_initiate', 'SeqAuto scan initiate'),)},
        ),
    ]
