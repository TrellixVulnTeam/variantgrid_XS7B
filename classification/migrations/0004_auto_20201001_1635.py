# Generated by Django 3.1 on 2020-10-01 07:05

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sync', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('classification', '0003_auto_20201001_1628'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='VariantClassificationModification',
            new_name='ClassificationModification',
        ),
    ]
