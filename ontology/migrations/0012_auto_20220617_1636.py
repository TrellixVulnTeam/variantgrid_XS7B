# Generated by Django 4.0.2 on 2022-06-17 07:06

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import psqlextra.backend.migrations.operations.add_default_partition
import psqlextra.backend.migrations.operations.create_partitioned_model
import psqlextra.models.partitioned
import psqlextra.types


class Migration(migrations.Migration):

    dependencies = [
        ('ontology', '0011_alter_oldontologytermrelation_dest_term_and_more'),
    ]

    operations = [
        psqlextra.backend.migrations.operations.create_partitioned_model.PostgresCreatePartitionedModel(
            name='OntologyTermRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('relation', models.TextField()),
                ('extra', models.JSONField(blank=True, null=True)),
                ('dest_term', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ontology.ontologyterm')),
                ('from_import', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ontology.ontologyimport')),
                ('source_term', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subject2', to='ontology.ontologyterm')),
            ],
            options={
                'unique_together': {('from_import', 'source_term', 'dest_term', 'relation')},
            },
            partitioning_options={
                'method': psqlextra.types.PostgresPartitioningMethod['LIST'],
                'key': ['from_import_id'],
            },
            bases=(psqlextra.models.partitioned.PostgresPartitionedModel,),
        ),
        psqlextra.backend.migrations.operations.add_default_partition.PostgresAddDefaultPartition(
            model_name='OntologyTermRelation',
            name='default',
        ),
    ]
