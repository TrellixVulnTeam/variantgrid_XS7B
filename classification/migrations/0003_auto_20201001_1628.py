# Generated by Django 3.1 on 2020-10-01 06:58

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('snpdb', '0002_initial_data'),
        ('flags', '0002_initial_data'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('analysis', '0002_initial_data'),
        ('annotation', '0003_initial_data'),
        ('classification', '0002_blat_keys'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='VariantClassification',
            new_name='Classification',
        ),
    ]
