# Generated by Django 3.1 on 2020-10-01 07:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0002_initial_data'),
    ]

    operations = [
        migrations.RenameField(
            model_name='analysisvariantclassification',
            old_name='variant_classification',
            new_name='classification',
        ),
    ]
