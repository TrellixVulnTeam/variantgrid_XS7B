# Generated by Django 3.1.3 on 2021-03-22 04:17

from django.db import migrations


def _one_off_change_analysis_tags(apps, schema_editor):
    TagNode = apps.get_model("analysis", "TagNode")
    THIS_ANALYSIS = 'T'
    TagNode.objects.filter(analysis_wide=True).update(mode=THIS_ANALYSIS)
    for node in TagNode.objects.filter(tag__isnull=False):
        node.tagnodetag_set.create(tag=node.tag)


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0024_auto_20210322_1447'),
    ]

    operations = [
        migrations.RunPython(_one_off_change_analysis_tags)
    ]
