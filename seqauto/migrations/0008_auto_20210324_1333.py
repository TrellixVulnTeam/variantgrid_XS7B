# Generated by Django 3.1.3 on 2021-03-24 03:03

import django.contrib.postgres.fields.ranges
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields
import seqauto.models.models_seqauto


class Migration(migrations.Migration):

    dependencies = [
        ('genes', '0022_auto_20210225_1521'),
        ('snpdb', '0026_auto_20210319_1231'),
        ('patients', '0001_initial'),
        ('seqauto', '0007_one_off_sequencing_run_valid'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExecSummaryReferenceRange2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('percent_20x', django.contrib.postgres.fields.ranges.DecimalRangeField(null=True)),
                ('percent_10x', django.contrib.postgres.fields.ranges.DecimalRangeField(null=True)),
                ('mean_coverage_across_genes', django.contrib.postgres.fields.ranges.DecimalRangeField()),
                ('mean_coverage_across_kit', django.contrib.postgres.fields.ranges.DecimalRangeField(null=True)),
                ('min_mean_coverage_across_kit', models.IntegerField(null=True)),
                ('min_percent_20x_kit', models.IntegerField(null=True)),
                ('uniformity_of_coverage', django.contrib.postgres.fields.ranges.DecimalRangeField()),
                ('percent_read_enrichment', django.contrib.postgres.fields.ranges.DecimalRangeField()),
                ('duplicated_alignable_reads', django.contrib.postgres.fields.ranges.DecimalRangeField()),
                ('median_insert', django.contrib.postgres.fields.ranges.DecimalRangeField()),
                ('ts_to_tv_ratio', django.contrib.postgres.fields.ranges.DecimalRangeField()),
                ('number_snps', django.contrib.postgres.fields.ranges.DecimalRangeField()),
                ('snp_dbsnp_percent', django.contrib.postgres.fields.ranges.DecimalRangeField()),
                ('number_indels', django.contrib.postgres.fields.ranges.DecimalRangeField()),
                ('indels_dbsnp_percent', django.contrib.postgres.fields.ranges.DecimalRangeField()),
            ],
        ),
        migrations.CreateModel(
            name='IlluminaIndexQC2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index', models.TextField()),
                ('project', models.TextField()),
                ('name', models.TextField()),
                ('reads', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='ReadQ302',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sequencer_read_id', models.IntegerField()),
                ('read', models.CharField(choices=[('R1', 'R1'), ('R2', 'R2'), ('I1', 'I1'), ('I2', 'I2')], max_length=2)),
                ('percent', models.FloatField()),
                ('is_index', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='SampleFromSequencingSample2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sample', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='snpdb.sample')),
            ],
        ),
        migrations.CreateModel(
            name='SeqAutoMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('severity', models.CharField(choices=[('D', 'DEBUG'), ('I', 'INFO'), ('W', 'WARNING'), ('E', 'ERROR')], max_length=1)),
                ('message', models.TextField(null=True)),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SeqAutoRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('path', models.TextField()),
                ('file_last_modified', models.FloatField(default=0.0)),
                ('hash', models.TextField()),
                ('data_state', models.CharField(choices=[('N', 'Non Existent'), ('D', 'Deleted'), ('R', 'Running'), ('S', 'Skipped'), ('E', 'Error'), ('C', 'Complete')], max_length=1)),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SequencingRunCurrentSampleSheet2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='SequencingSample2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sample_id', models.TextField()),
                ('sample_name', models.TextField(null=True)),
                ('sample_project', models.TextField(null=True)),
                ('sample_number', models.IntegerField()),
                ('lane', models.IntegerField(null=True)),
                ('barcode', models.TextField()),
                ('is_control', models.BooleanField(default=False)),
                ('failed', models.BooleanField(default=False)),
                ('automatically_process', models.BooleanField(default=True)),
                ('enrichment_kit', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='seqauto.enrichmentkit')),
            ],
        ),
        migrations.CreateModel(
            name='SequencingSampleData2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('column', models.TextField()),
                ('value', models.TextField(null=True)),
                ('sequencing_sample', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seqauto.sequencingsample2')),
            ],
        ),
        migrations.CreateModel(
            name='UnalignedReads2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sequencing_sample', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seqauto.sequencingsample2')),
            ],
            bases=(models.Model, ),
        ),
        migrations.CreateModel(
            name='VCFFromSequencingRun2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vcf', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='snpdb.vcf')),
            ],
        ),
        migrations.RemoveField(
            model_name='seqautorunevent',
            name='seqauto_run',
        ),
        migrations.RemoveField(
            model_name='sequencingrunmodification',
            name='seqauto_run_event',
        ),
        migrations.RemoveField(
            model_name='sequencingrunmodification',
            name='sequencing_run',
        ),
        migrations.RemoveField(
            model_name='sequencingrunmodification',
            name='user',
        ),
        migrations.RemoveField(
            model_name='sequencingrunwiki',
            name='sequencing_run',
        ),
        migrations.RemoveField(
            model_name='sequencingrunwiki',
            name='wiki_ptr',
        ),
        migrations.CreateModel(
            name='BamFile2',
            fields=[
                ('seqautorecord_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='seqauto.seqautorecord')),
                ('name', models.TextField()),
                ('aligner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seqauto.aligner')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
            bases=('seqauto.seqautorecord',),
        ),
        migrations.CreateModel(
            name='Fastq2',
            fields=[
                ('seqautorecord_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='seqauto.seqautorecord')),
                ('name', models.TextField()),
                ('read', models.CharField(choices=[('R1', 'R1'), ('R2', 'R2')], max_length=2)),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
            bases=('seqauto.seqautorecord',),
        ),
        migrations.CreateModel(
            name='FastQC2',
            fields=[
                ('seqautorecord_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='seqauto.seqautorecord')),
                ('total_sequences', models.IntegerField(null=True)),
                ('filtered_sequences', models.IntegerField(null=True)),
                ('gc', models.IntegerField(null=True)),
                ('fastq', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='seqauto.fastq2')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
            bases=('seqauto.seqautorecord',),
        ),
        migrations.CreateModel(
            name='Flagstats2',
            fields=[
                ('seqautorecord_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='seqauto.seqautorecord')),
                ('total', models.IntegerField(null=True)),
                ('read1', models.IntegerField(null=True)),
                ('read2', models.IntegerField(null=True)),
                ('mapped', models.IntegerField(null=True)),
                ('properly_paired', models.IntegerField(null=True)),
                ('bam_file', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='seqauto.bamfile2')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
            bases=('seqauto.seqautorecord',),
        ),
        migrations.CreateModel(
            name='IlluminaFlowcellQC2',
            fields=[
                ('seqautorecord_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='seqauto.seqautorecord')),
                ('mean_cluster_density', models.IntegerField(null=True)),
                ('mean_pf_cluster_density', models.IntegerField(null=True)),
                ('total_clusters', models.IntegerField(null=True)),
                ('total_pf_clusters', models.IntegerField(null=True)),
                ('percentage_of_clusters_pf', models.FloatField(null=True)),
                ('aligned_to_phix', models.FloatField(null=True)),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
            bases=('seqauto.seqautorecord',),
        ),
        migrations.CreateModel(
            name='QC2',
            fields=[
                ('seqautorecord_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='seqauto.seqautorecord')),
                ('bam_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seqauto.bamfile2')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
            bases=('seqauto.seqautorecord',),
        ),
        migrations.CreateModel(
            name='QCExecSummary2',
            fields=[
                ('seqautorecord_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='seqauto.seqautorecord')),
                ('percent_20x_kit', models.FloatField(null=True)),
                ('percent_500x', models.FloatField(null=True)),
                ('percent_250x', models.FloatField(null=True)),
                ('percent_20x', models.FloatField(null=True)),
                ('percent_10x', models.FloatField(null=True)),
                ('mean_coverage_across_genes', models.FloatField()),
                ('mean_coverage_across_kit', models.FloatField()),
                ('uniformity_of_coverage', models.FloatField()),
                ('percent_read_enrichment', models.FloatField()),
                ('duplicated_alignable_reads', models.FloatField()),
                ('median_insert', models.FloatField()),
                ('ts_to_tv_ratio', models.FloatField()),
                ('number_snps', models.IntegerField()),
                ('snp_dbsnp_percent', models.FloatField()),
                ('number_indels', models.IntegerField()),
                ('indels_dbsnp_percent', models.FloatField()),
                ('gene_list', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='genes.genelist')),
                ('qc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seqauto.qc2')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
            bases=('seqauto.seqautorecord',),
        ),
        migrations.CreateModel(
            name='QCGeneCoverage2',
            fields=[
                ('seqautorecord_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='seqauto.seqautorecord')),
                ('gene_coverage_collection', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='genes.genecoveragecollection')),
                ('qc', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='seqauto.qc2')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
            bases=('seqauto.seqautorecord',),
        ),
        migrations.CreateModel(
            name='QCGeneList2',
            fields=[
                ('seqautorecord_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='seqauto.seqautorecord')),
                ('custom_text_gene_list', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='genes.customtextgenelist')),
                ('qc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seqauto.qc2')),
                ('sample_gene_list', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='genes.samplegenelist')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
            bases=('seqauto.seqautorecord',),
        ),
        migrations.CreateModel(
            name='SampleSheet2',
            fields=[
                ('seqautorecord_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='seqauto.seqautorecord')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
            bases=('seqauto.seqautorecord',),
        ),
        migrations.CreateModel(
            name='SampleSheetCombinedVCFFile2',
            fields=[
                ('seqautorecord_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='seqauto.seqautorecord')),
                ('sample_sheet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seqauto.samplesheet2')),
                ('variant_caller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seqauto.variantcaller')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
            bases=('seqauto.seqautorecord', ),
        ),
        migrations.CreateModel(
            name='SequencingRun2',
            fields=[
                ('seqautorecord_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, to='seqauto.seqautorecord')),
                ('name', models.TextField(primary_key=True, serialize=False)),
                ('gold_standard', models.BooleanField(default=False)),
                ('bad', models.BooleanField(default=False)),
                ('hidden', models.BooleanField(default=False)),
                ('ready', models.BooleanField(default=False)),
                ('legacy', models.BooleanField(default=False)),
                ('has_basecalls', models.BooleanField(default=False)),
                ('has_interop', models.BooleanField(default=False)),
                ('enrichment_kit', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='seqauto.enrichmentkit')),
                ('experiment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='seqauto.experiment')),
                ('fake_data', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='patients.fakedata')),
                ('sequencer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seqauto.sequencer')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
            bases=('seqauto.seqautorecord',),
        ),
        migrations.CreateModel(
            name='VCFFile2',
            fields=[
                ('seqautorecord_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='seqauto.seqautorecord')),
                ('bam_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seqauto.bamfile2')),
                ('variant_caller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seqauto.variantcaller')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
            bases=('seqauto.seqautorecord', ),
        ),
        migrations.DeleteModel(
            name='JobScript',
        ),
        migrations.DeleteModel(
            name='SeqAutoRunEvent',
        ),
        migrations.DeleteModel(
            name='SequencingRunModification',
        ),
        migrations.DeleteModel(
            name='SequencingRunWiki',
        ),
        migrations.AddField(
            model_name='seqautomessage',
            name='record',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seqauto.seqautorecord'),
        ),
        migrations.AddField(
            model_name='seqautomessage',
            name='seqauto_run',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seqauto.seqautorun'),
        ),
        migrations.AddField(
            model_name='samplefromsequencingsample2',
            name='sequencing_sample',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='seqauto.sequencingsample2'),
        ),
        migrations.AddField(
            model_name='vcffromsequencingrun2',
            name='sequencing_run',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='seqauto.sequencingrun2'),
        ),
        migrations.AddField(
            model_name='unalignedreads2',
            name='fastq_r1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fastq_r1', to='seqauto.fastq2'),
        ),
        migrations.AddField(
            model_name='unalignedreads2',
            name='fastq_r2',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='fastq_r2', to='seqauto.fastq2'),
        ),
        migrations.AddField(
            model_name='sequencingsample2',
            name='sample_sheet',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seqauto.samplesheet2'),
        ),
        migrations.AddField(
            model_name='sequencingruncurrentsamplesheet2',
            name='sample_sheet',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='seqauto.samplesheet2'),
        ),
        migrations.AddField(
            model_name='sequencingruncurrentsamplesheet2',
            name='sequencing_run',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='seqauto.sequencingrun2'),
        ),
        migrations.AddField(
            model_name='samplesheet2',
            name='sequencing_run',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seqauto.sequencingrun2'),
        ),
        migrations.AddField(
            model_name='readq302',
            name='illumina_flowcell_qc',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seqauto.illuminaflowcellqc2'),
        ),
        migrations.AddField(
            model_name='qc2',
            name='vcf_file',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seqauto.vcffile2'),
        ),
        migrations.AddField(
            model_name='illuminaindexqc2',
            name='illumina_flowcell_qc',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seqauto.illuminaflowcellqc2'),
        ),
        migrations.AddField(
            model_name='illuminaflowcellqc2',
            name='sample_sheet',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='seqauto.samplesheet2'),
        ),
        migrations.AddField(
            model_name='fastq2',
            name='sequencing_sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='seqauto.sequencingsample2'),
        ),
        migrations.AddField(
            model_name='execsummaryreferencerange2',
            name='exec_summary',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='seqauto.qcexecsummary2'),
        ),
        migrations.AddField(
            model_name='bamfile2',
            name='unaligned_reads',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='seqauto.unalignedreads2'),
        ),
    ]
