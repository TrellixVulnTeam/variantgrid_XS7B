# Generated by Django 3.1 on 2020-11-26 04:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0008_analysislock'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysis',
            name='version',
            field=models.IntegerField(default=0),
        ),
    ]
