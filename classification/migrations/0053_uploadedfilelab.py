# Generated by Django 3.2.6 on 2021-09-02 02:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('snpdb', '0046_lab_upload_auto_pattern'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('classification', '0052_one_off_fix_legacy_classification_alignment_gap_hgvs_matching'),
    ]

    operations = [
        migrations.CreateModel(
            name='UploadedFileLab',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('url', models.TextField()),
                ('filename', models.TextField()),
                ('comment', models.TextField(default='')),
                ('status', models.CharField(choices=[('P', 'Pending'), ('AP', 'Automatically-Processed'), ('MP', 'Processed'), ('E', 'Error')], default='P', max_length=2)),
                ('lab', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snpdb.lab')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
