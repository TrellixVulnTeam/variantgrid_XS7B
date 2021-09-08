# Generated by Django 3.1 on 2020-10-01 07:38

from django.db import migrations


def rename_variant_classification(apps, schema_editor):
    FlagTypeContext = apps.get_model("flags", "FlagTypeContext")
    FlagType = apps.get_model("flags", "FlagType")
    FlagTypeResolution = apps.get_model("flags", "FlagTypeResolution")
    Flag = apps.get_model("flags", "Flag")
    FlagCollection = apps.get_model("flags", "FlagCollection")

    old_context = FlagTypeContext.objects.filter(id="variant_classification").first()
    if old_context:
        classification_context = FlagTypeContext.objects.create(id='classification', label='Flags for Classifications')
        FlagCollection.objects.filter(context=old_context).update(context=classification_context)
        FlagType.objects.filter(context=old_context).update(context=classification_context)

    for flag_type_value in FlagType.objects.filter(id__startswith="variant_classification").values():
        old_id = flag_type_value["id"]
        flag_type_value["id"] = old_id.replace("variant_classification", "classification")
        ft = FlagType.objects.create(**flag_type_value)

        Flag.objects.filter(flag_type_id=old_id).update(flag_type=ft)
        FlagTypeResolution.objects.filter(flag_type_id=old_id).update(flag_type=ft)

    FlagType.objects.filter(id__startswith="variant_classification").delete()


class Migration(migrations.Migration):

    dependencies = [
        ('flags', '0002_initial_data'),
    ]

    operations = [
        migrations.RunPython(rename_variant_classification)
    ]
