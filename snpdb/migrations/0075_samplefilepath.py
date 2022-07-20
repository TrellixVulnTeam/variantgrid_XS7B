# Generated by Django 4.0.2 on 2022-07-18 06:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('snpdb', '0074_custom_columns_for_new_vep_columns'),
    ]

    operations = [
        migrations.CreateModel(
            name='SampleFilePath',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_type', models.CharField(blank=True, choices=[('B', 'BAM'), ('C', 'CRAM'), ('E', 'BED'), ('V', 'VCF')], max_length=1, null=True)),
                ('label', models.TextField(blank=True, null=True)),
                ('file_path', models.TextField(blank=True, null=True)),
                ('sample', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snpdb.sample')),
            ],
        ),
    ]
