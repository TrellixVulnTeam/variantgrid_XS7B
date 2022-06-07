# Generated by Django 4.0.2 on 2022-04-05 06:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classification', '0065_alter_uploadedclassificationsunmapped_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='classificationimportrun',
            name='from_file',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='classification.uploadedclassificationsunmapped'),
        ),
        migrations.AlterField(
            model_name='uploadedclassificationsunmapped',
            name='status',
            field=models.CharField(choices=[('MA', 'Manual'), ('P', 'Pending'), ('M', 'Mapping'), ('I', 'Importing'), ('V', 'Validated'), ('E', 'Error'), ('MP', 'Processed')], default='P', max_length=2),
        ),
    ]
