# Generated by Django 3.1.6 on 2021-02-11 04:18

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('classification', '0020_auto_20210202_1531'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='conditiontext',
            name='last_edited_by',
        ),
        migrations.RemoveField(
            model_name='conditiontext',
            name='min_auto_match_score',
        ),
        migrations.AddField(
            model_name='conditiontextmatch',
            name='last_edited_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
