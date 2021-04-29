# Generated by Django 3.1.3 on 2021-04-29 05:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annotation', '0029_one_off_fix_annotation_link_transcript'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variantannotation',
            name='impact',
            field=models.CharField(blank=True, choices=[('O', 'MODIFIER'), ('L', 'LOW'), ('M', 'MODERATE'), ('*', 'MODERATE*'), ('H', 'HIGH')], max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='varianttranscriptannotation',
            name='impact',
            field=models.CharField(blank=True, choices=[('O', 'MODIFIER'), ('L', 'LOW'), ('M', 'MODERATE'), ('*', 'MODERATE*'), ('H', 'HIGH')], max_length=1, null=True),
        ),
    ]
