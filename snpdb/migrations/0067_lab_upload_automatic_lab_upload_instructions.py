# Generated by Django 4.0.2 on 2022-04-04 04:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('snpdb', '0066_remove_lab_upload_auto_pattern'),
    ]

    operations = [
        migrations.AddField(
            model_name='lab',
            name='upload_automatic',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AddField(
            model_name='lab',
            name='upload_instructions',
            field=models.TextField(blank=True, default=''),
        ),
    ]
