# Generated by Django 4.0.3 on 2022-05-17 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annotation', '0054_variantannotationversion_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variantannotation',
            name='lof',
            field=models.CharField(blank=True, choices=[('l', 'Low Confidence'), ('h', 'High Confidence'), ('o', 'Other Splice')], max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='varianttranscriptannotation',
            name='lof',
            field=models.CharField(blank=True, choices=[('l', 'Low Confidence'), ('h', 'High Confidence'), ('o', 'Other Splice')], max_length=1, null=True),
        ),
    ]