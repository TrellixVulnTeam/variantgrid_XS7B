# Generated by Django 3.1 on 2020-09-29 05:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields
import library.django_utils.django_file_system_storage


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('expression', '0001_initial'),
        ('genes', '0001_initial'),
        ('annotation', '0002_auto_20200929_1503'),
        ('snpdb', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('variantclassification', '0001_initial'),
        ('patients', '0001_initial'),
        ('seqauto', '0001_initial'),
        ('pedigree', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ToolVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('version', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UploadedFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('path', models.TextField(null=True)),
                ('uploaded_file', models.FileField(max_length=256, null=True, storage=library.django_utils.django_file_system_storage.PrivateUploadStorage(), upload_to='')),
                ('md5_hash', models.CharField(max_length=32, null=True)),
                ('file_type', models.CharField(choices=[('B', 'BED'), ('L', 'Clinvar'), ('T', 'Clinvar Citations'), ('C', 'CuffDiff'), ('G', 'Gene List'), ('O', 'Gene Coverage'), ('I', 'Liftover'), ('P', 'Pedigree'), ('R', 'Patient Records'), ('V', 'VCF'), ('Y', 'VCF - Insert variants only (no samples etc)'), ('S', 'Variant Classifications')], max_length=1, null=True)),
                ('import_source', models.CharField(choices=[('A', 'API'), ('C', 'Command Line'), ('S', 'SeqAuto'), ('W', 'Web'), ('U', 'Web Upload')], max_length=1)),
                ('name', models.TextField()),
                ('visible', models.BooleanField(default=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UploadedVCF',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('max_variant', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='snpdb.variant')),
            ],
        ),
        migrations.CreateModel(
            name='UploadPipeline',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('C', 'Created'), ('P', 'Processing'), ('E', 'Error'), ('S', 'Success'), ('K', 'Skipped'), ('T', 'Terminated Early'), ('Z', 'Timed Out')], default='C', max_length=1)),
                ('items_processed', models.BigIntegerField(null=True)),
                ('processing_seconds_wall_time', models.IntegerField(null=True)),
                ('processing_seconds_cpu_time', models.IntegerField(null=True)),
                ('progress_status', models.TextField(null=True)),
                ('progress_percent', models.FloatField(default=0)),
                ('celery_task', models.CharField(max_length=36, null=True)),
                ('uploaded_file', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='upload.uploadedfile')),
            ],
        ),
        migrations.CreateModel(
            name='UploadStep',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('sort_order', models.IntegerField()),
                ('status', models.CharField(choices=[('C', 'Created'), ('P', 'Processing'), ('E', 'Error'), ('S', 'Success'), ('K', 'Skipped'), ('T', 'Terminated Early'), ('Z', 'Timed Out')], default='C', max_length=1)),
                ('origin', models.CharField(choices=[('A', 'User Addition'), ('I', 'Import Task Factory')], default='I', max_length=1)),
                ('items_to_process', models.BigIntegerField(default=0)),
                ('items_processed', models.IntegerField(null=True)),
                ('error_message', models.TextField()),
                ('input_filename', models.TextField()),
                ('output_filename', models.TextField()),
                ('start_date', models.DateTimeField(null=True)),
                ('end_date', models.DateTimeField(null=True)),
                ('task_type', models.CharField(choices=[('C', 'Celery'), ('Q', 'SQL'), ('T', 'Tool')], max_length=1)),
                ('pipeline_stage', models.CharField(choices=[('U', 'Insert Unknown Variants'), ('D', 'Data Insertion'), ('A', 'Annotation Complete'), ('F', 'Finish')], max_length=1, null=True)),
                ('pipeline_stage_dependency', models.CharField(choices=[('U', 'Insert Unknown Variants'), ('D', 'Data Insertion'), ('A', 'Annotation Complete'), ('F', 'Finish')], max_length=1, null=True)),
                ('script', models.TextField()),
                ('child_script', models.TextField(null=True)),
                ('import_variant_table', models.TextField(blank=True, null=True)),
                ('celery_task', models.CharField(max_length=36, null=True)),
                ('output_text', models.TextField(null=True)),
                ('input_upload_step', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='upload.uploadstep')),
                ('parent_upload_step', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='substep_set', to='upload.uploadstep')),
                ('tool_version', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='upload.toolversion')),
                ('upload_pipeline', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='upload.uploadpipeline')),
            ],
        ),
        migrations.CreateModel(
            name='VCFImportInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('severity', models.CharField(choices=[('W', 'WARNING'), ('E', 'ERROR')], default='W', max_length=1)),
                ('accepted_date', models.DateTimeField(null=True)),
                ('upload_step', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='upload.uploadstep')),
            ],
        ),
        migrations.CreateModel(
            name='ModifiedImportedVariants',
            fields=[
                ('vcfimportinfo_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='upload.vcfimportinfo')),
            ],
            bases=('upload.vcfimportinfo',),
        ),
        migrations.CreateModel(
            name='VCFSkippedContigs',
            fields=[
                ('vcfimportinfo_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='upload.vcfimportinfo')),
            ],
            bases=('upload.vcfimportinfo',),
        ),
        migrations.CreateModel(
            name='VCFSkippedGVCFNonVarBlocks',
            fields=[
                ('vcfimportinfo_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='upload.vcfimportinfo')),
                ('num_skipped', models.IntegerField()),
            ],
            bases=('upload.vcfimportinfo',),
        ),
        migrations.CreateModel(
            name='VCFImporter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('version', models.IntegerField()),
                ('vcf_parser', models.TextField()),
                ('vcf_parser_version', models.TextField()),
                ('code_git_hash', models.TextField()),
            ],
            options={
                'unique_together': {('name', 'version', 'vcf_parser', 'vcf_parser_version', 'code_git_hash')},
            },
        ),
        migrations.CreateModel(
            name='UploadStepMultiFileOutput',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('output_filename', models.TextField()),
                ('items_to_process', models.IntegerField()),
                ('upload_step', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='upload.uploadstep')),
            ],
        ),
        migrations.CreateModel(
            name='UploadSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_filter_method', models.CharField(choices=[('D', 'days'), ('R', 'records')], default='R', max_length=1)),
                ('time_filter_value', models.IntegerField(default=5)),
                ('show_all', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UploadedVCFPendingAnnotation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('finished', models.DateTimeField(null=True)),
                ('schedule_pipeline_stage_steps_celery_task', models.CharField(max_length=36, null=True)),
                ('uploaded_vcf', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='upload.uploadedvcf')),
            ],
        ),
        migrations.AddField(
            model_name='uploadedvcf',
            name='upload_pipeline',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='upload.uploadpipeline'),
        ),
        migrations.AddField(
            model_name='uploadedvcf',
            name='uploaded_file',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='upload.uploadedfile'),
        ),
        migrations.AddField(
            model_name='uploadedvcf',
            name='vcf',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='snpdb.vcf'),
        ),
        migrations.AddField(
            model_name='uploadedvcf',
            name='vcf_importer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='upload.vcfimporter'),
        ),
        migrations.CreateModel(
            name='UploadedVariantClassificationImport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uploaded_file', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='upload.uploadedfile')),
                ('variant_classification_import', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='variantclassification.variantclassificationimport')),
            ],
        ),
        migrations.CreateModel(
            name='UploadedPedFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ped_file', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='pedigree.pedfile')),
                ('uploaded_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='upload.uploadedfile')),
            ],
        ),
        migrations.CreateModel(
            name='UploadedPatientRecords',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('patient_records', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='patients.patientrecords')),
                ('uploaded_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='upload.uploadedfile')),
            ],
        ),
        migrations.CreateModel(
            name='UploadedManualVariantEntryCollection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('collection', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='annotation.manualvariantentrycollection')),
                ('uploaded_file', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='upload.uploadedfile')),
            ],
        ),
        migrations.CreateModel(
            name='UploadedLiftover',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('liftover', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='snpdb.liftover')),
                ('uploaded_file', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='upload.uploadedfile')),
            ],
        ),
        migrations.CreateModel(
            name='UploadedGeneList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gene_list', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='genes.genelist')),
                ('uploaded_file', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='upload.uploadedfile')),
            ],
        ),
        migrations.CreateModel(
            name='UploadedGeneCoverage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gene_coverage_collection', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='genes.genecoveragecollection')),
                ('sample', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='snpdb.sample')),
                ('uploaded_file', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='upload.uploadedfile')),
            ],
        ),
        migrations.CreateModel(
            name='UploadedExpressionFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('format', models.CharField(choices=[('C', 'CuffDiff')], max_length=1)),
                ('annotation_level', models.CharField(choices=[('T', 'Transcript'), ('G', 'Gene Symbol')], max_length=1)),
                ('cuff_diff_file', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='expression.cuffdifffile')),
                ('uploaded_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='upload.uploadedfile')),
            ],
        ),
        migrations.CreateModel(
            name='UploadedClinVarVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clinvar_version', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='annotation.clinvarversion')),
                ('uploaded_file', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='upload.uploadedfile')),
            ],
        ),
        migrations.CreateModel(
            name='UploadedClinVarCitations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('md5_hash', models.CharField(max_length=32)),
                ('clinvar_citations_collection', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='annotation.clinvarcitationscollection')),
                ('uploaded_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='upload.uploadedfile')),
            ],
        ),
        migrations.CreateModel(
            name='UploadedBed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('genomic_intervals_collection', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='snpdb.genomicintervalscollection')),
                ('uploaded_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='upload.uploadedfile')),
            ],
        ),
        migrations.CreateModel(
            name='BackendVCF',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('combo_vcf', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='seqauto.samplesheetcombinedvcffile')),
                ('uploaded_vcf', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='upload.uploadedvcf')),
                ('vcf_file', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='seqauto.vcffile')),
            ],
        ),
        migrations.CreateModel(
            name='VCFSkippedContig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contig', models.TextField()),
                ('num_skipped', models.IntegerField()),
                ('import_info', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='upload.vcfskippedcontigs')),
            ],
        ),
        migrations.CreateModel(
            name='ModifiedImportedVariant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_multiallelic', models.TextField(null=True)),
                ('old_variant', models.TextField(null=True)),
                ('old_variant_formatted', models.TextField(null=True)),
                ('variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snpdb.variant')),
                ('import_info', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='upload.modifiedimportedvariants')),
            ],
        ),
    ]
