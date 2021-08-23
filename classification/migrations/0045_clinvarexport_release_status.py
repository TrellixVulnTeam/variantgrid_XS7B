# Generated by Django 3.1.6 on 2021-08-02 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classification', '0044_auto_20210730_1252'),
    ]

    operations = [
        migrations.AddField(
            model_name='clinvarexport',
            name='release_status',
            field=models.CharField(choices=[('R', 'Release When Ready'), ('H', 'On Hold')], default='R', max_length=1),
        ),
    ]
