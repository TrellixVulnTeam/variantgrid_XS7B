# Generated by Django 3.1 on 2020-11-24 11:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pathtests', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pathologytestomim',
            name='mim_morbid_alias',
        ),
        migrations.RemoveField(
            model_name='pathologytestomim',
            name='pathology_test',
        ),
        migrations.RemoveField(
            model_name='pathologytestpanelapppanel',
            name='panel_app_panel',
        ),
        migrations.RemoveField(
            model_name='pathologytestpanelapppanel',
            name='pathology_test',
        ),
        migrations.DeleteModel(
            name='PathologyTestHPO',
        ),
        migrations.DeleteModel(
            name='PathologyTestOMIM',
        ),
        migrations.DeleteModel(
            name='PathologyTestPanelAppPanel',
        ),
    ]
