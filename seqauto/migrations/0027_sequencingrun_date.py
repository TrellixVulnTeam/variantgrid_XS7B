# Generated by Django 3.1.3 on 2021-06-15 02:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seqauto', '0026_auto_20210524_1225'),
    ]

    operations = [
        migrations.AddField(
            model_name='sequencingrun',
            name='date',
            field=models.DateField(null=True),
        ),
    ]