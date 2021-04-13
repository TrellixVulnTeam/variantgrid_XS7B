# Generated by Django 3.1.3 on 2021-04-09 04:08

from django.db import migrations

from manual.operations.manual_operations import ManualOperation


def _one_off_variant_tags(apps, schema_editor):
    VariantTag = apps.get_model("analysis", "VariantTag")

    records = []
    # All existing tags will have analysis set (was only just set nullable)
    for vt in VariantTag.objects.all():
        vt.genome_build = vt.analysis.genome_build
        records.append(vt)

    if records:
        VariantTag.objects.bulk_update(records, ["genome_build"], batch_size=2000)


def _test_has_variant_tags(apps):
    VariantTag = apps.get_model("analysis", "VariantTag")
    return VariantTag.objects.all().exists()


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0032_auto_20210409_1333'),
    ]

    operations = [
        migrations.RunPython(_one_off_variant_tags),
        ManualOperation(task_id=ManualOperation.task_id_manage(["fix_variant_tag_permissions"]),
                        test=_test_has_variant_tags)
    ]
