# Generated by Django 3.1.3 on 2021-04-12 05:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0034_auto_20210409_1724'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tagnode',
            name='mode',
            field=models.CharField(choices=[('P', 'Parent'), ('T', 'This Analysis'), ('L', 'All Tags')], default='P', max_length=1),
        ),
    ]
