# Generated by Django 3.1.6 on 2021-03-12 00:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classification', '0024_new_ekey_clinvar_conflicting_clinical_significance'),
    ]

    operations = [
        migrations.AddField(
            model_name='classification',
            name='condition_resolution',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
