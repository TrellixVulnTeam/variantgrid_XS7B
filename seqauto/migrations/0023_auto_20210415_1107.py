# Generated by Django 3.1.3 on 2021-04-15 01:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('seqauto', '0022_exec_summary_graphs_qc_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='samplefromsequencingsample',
            name='sequencing_sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seqauto.sequencingsample'),
        ),
    ]
