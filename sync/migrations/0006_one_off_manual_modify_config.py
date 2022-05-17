# Generated by Django 4.0.2 on 2022-05-11 06:35

from django.db import migrations

from manual.operations.manual_operations import ManualOperation


def _check_has_sync_destination(apps):
    SyncDestination = apps.get_model("sync", "SyncDestination")
    return SyncDestination.objects.filter(enabled=True).exists()


class Migration(migrations.Migration):
    dependencies = [
        ('sync', '0005_syncdestination_enabled'),
    ]

    operations = [
        ManualOperation.operation_other(args=[
            "Modify /etc/variantgrid/settings_config.json - SYNC uses keys to allow multiple config",
            "In Admin, modify sync.SyncDestination.config and add 'sync_details' corresponding to SYNC keys"
        ], test=_check_has_sync_destination)
    ]