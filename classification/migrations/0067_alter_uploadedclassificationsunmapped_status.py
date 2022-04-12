# Generated by Django 4.0.2 on 2022-04-12 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classification', '0066_classificationimportrun_from_file_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadedclassificationsunmapped',
            name='status',
            field=models.CharField(choices=[('MA', 'Manual Review Pending'), ('P', 'Pending'), ('M', 'Mapping'), ('I', 'Importing'), ('V', 'Validated'), ('E', 'Error'), ('MP', 'Processed')], default='P', max_length=2),
        ),
    ]
