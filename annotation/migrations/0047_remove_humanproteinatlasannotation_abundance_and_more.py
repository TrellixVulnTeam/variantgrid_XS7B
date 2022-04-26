# Generated by Django 4.0.3 on 2022-04-26 02:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annotation', '0046_one_off_migrate_human_protein_atlas'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='humanproteinatlasannotation',
            name='abundance',
        ),
        migrations.AlterField(
            model_name='humanproteinatlasannotation',
            name='value',
            field=models.FloatField(),
        ),
    ]