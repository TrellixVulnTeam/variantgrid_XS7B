# Generated by Django 3.2.6 on 2021-09-01 05:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('snpdb', '0045_one_off_reference_variant_fixes'),
    ]

    operations = [
        migrations.AddField(
            model_name='lab',
            name='upload_auto_pattern',
            field=models.TextField(blank=True, default=''),
        ),
    ]
