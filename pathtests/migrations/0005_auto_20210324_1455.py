# Generated by Django 3.1.3 on 2021-03-24 04:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('seqauto', '0009_copy_to_models_v2'),
        ('pathtests', '0004_auto_20210121_1754'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pathologytestorder',
            name='sequencing_run',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='seqauto.sequencingrun2'),
        ),
    ]
