# Generated by Django 3.1 on 2021-04-15 11:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0035_auto_20210412_1516'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysisnode',
            name='cloned_from',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='analysis.nodeversion'),
        ),
    ]
