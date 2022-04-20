# Generated by Django 3.1 on 2020-10-30 03:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('genes', '0002_initial_data'),
        ('manual', '0002_deployment'),
    ]

    operations = [
        # Remove "gene_name" from TranscriptVersion.data JSON (fill in from relation)
        migrations.RunSQL("update genes_transcriptversion set data = data - 'gene_name';"),
    ]
