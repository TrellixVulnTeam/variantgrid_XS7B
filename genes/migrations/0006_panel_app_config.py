# Generated by Django 3.1 on 2020-11-24 12:03

from django.db import migrations


def one_off_delete_old_panel_app_cached_web_resource(apps, schema_editor):
    CachedWebResource = apps.get_model("annotation", "CachedWebResource")
    CachedWebResource.objects.filter(name='PanelAppPanels').delete()


def panel_app_config(apps, schema_editor):
    PanelAppServer = apps.get_model("genes", "PanelAppServer")

    PANEL_APP_SERVERS = [
        {"name": "Genomics England PanelApp",
         "url": "https://panelapp.genomicsengland.co.uk",
         "icon_css_class": "panel-app-england-icon"},
        {"name": "PanelApp Australia",
         "url": "https://panelapp.agha.umccr.org",
         "icon_css_class": "panel-app-australia-icon"},
    ]
    for kwargs in PANEL_APP_SERVERS:
        PanelAppServer.objects.create(**kwargs)


class Migration(migrations.Migration):

    dependencies = [
        ('genes', '0005_auto_20201125_0104'),
    ]

    operations = [
        migrations.RunPython(one_off_delete_old_panel_app_cached_web_resource),
        migrations.RunPython(panel_app_config),
    ]
