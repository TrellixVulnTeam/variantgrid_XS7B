# Generated by Django 3.1.3 on 2021-03-22 04:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0025_one_off_change_analysis_tags'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tagnode',
            name='analysis_wide',
        ),
        migrations.RemoveField(
            model_name='tagnode',
            name='tag',
        ),
    ]
