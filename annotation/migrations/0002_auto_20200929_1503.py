# Generated by Django 3.1 on 2020-09-29 05:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('annotation', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('patients', '0001_initial'),
        ('snpdb', '0001_initial'),
        ('genes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='varianttranscriptannotation',
            name='gene',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='genes.gene'),
        ),
        migrations.AddField(
            model_name='varianttranscriptannotation',
            name='transcript',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='genes.transcript'),
        ),
        migrations.AddField(
            model_name='varianttranscriptannotation',
            name='transcript_version',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='genes.transcriptversion'),
        ),
        migrations.AddField(
            model_name='varianttranscriptannotation',
            name='variant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snpdb.variant'),
        ),
        migrations.AddField(
            model_name='varianttranscriptannotation',
            name='version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.variantannotationversion'),
        ),
        migrations.AddField(
            model_name='variantgeneoverlap',
            name='annotation_run',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.annotationrun'),
        ),
        migrations.AddField(
            model_name='variantgeneoverlap',
            name='gene',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='genes.gene'),
        ),
        migrations.AddField(
            model_name='variantgeneoverlap',
            name='variant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snpdb.variant'),
        ),
        migrations.AddField(
            model_name='variantgeneoverlap',
            name='version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.variantannotationversion'),
        ),
        migrations.AddField(
            model_name='variantannotationversion',
            name='gene_annotation_release',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='genes.geneannotationrelease'),
        ),
        migrations.AddField(
            model_name='variantannotationversion',
            name='genome_build',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snpdb.genomebuild'),
        ),
        migrations.AddField(
            model_name='variantannotation',
            name='annotation_run',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.annotationrun'),
        ),
        migrations.AddField(
            model_name='variantannotation',
            name='gene',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='genes.gene'),
        ),
        migrations.AddField(
            model_name='variantannotation',
            name='transcript',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='genes.transcript'),
        ),
        migrations.AddField(
            model_name='variantannotation',
            name='transcript_version',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='genes.transcriptversion'),
        ),
        migrations.AddField(
            model_name='variantannotation',
            name='variant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snpdb.variant'),
        ),
        migrations.AddField(
            model_name='variantannotation',
            name='version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.variantannotationversion'),
        ),
        migrations.AddField(
            model_name='textphenotypesentence',
            name='phenotype_description',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.phenotypedescription'),
        ),
        migrations.AddField(
            model_name='textphenotypesentence',
            name='text_phenotype',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.textphenotype'),
        ),
        migrations.AddField(
            model_name='textphenotypematch',
            name='gene_symbol',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='genes.genesymbol'),
        ),
        migrations.AddField(
            model_name='textphenotypematch',
            name='hpo',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='annotation.humanphenotypeontology'),
        ),
        migrations.AddField(
            model_name='textphenotypematch',
            name='omim_alias',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='annotation.mimmorbidalias'),
        ),
        migrations.AddField(
            model_name='textphenotypematch',
            name='text_phenotype',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.textphenotype'),
        ),
        migrations.AddField(
            model_name='samplevariantannotationstatspassingfilter',
            name='sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snpdb.sample'),
        ),
        migrations.AddField(
            model_name='samplevariantannotationstatspassingfilter',
            name='variant_annotation_version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.variantannotationversion'),
        ),
        migrations.AddField(
            model_name='samplevariantannotationstats',
            name='sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snpdb.sample'),
        ),
        migrations.AddField(
            model_name='samplevariantannotationstats',
            name='variant_annotation_version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.variantannotationversion'),
        ),
        migrations.AddField(
            model_name='sampleensemblgeneannotationstatspassingfilter',
            name='ensembl_gene_annotation_version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.ensemblgeneannotationversion'),
        ),
        migrations.AddField(
            model_name='sampleensemblgeneannotationstatspassingfilter',
            name='sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snpdb.sample'),
        ),
        migrations.AddField(
            model_name='sampleensemblgeneannotationstats',
            name='ensembl_gene_annotation_version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.ensemblgeneannotationversion'),
        ),
        migrations.AddField(
            model_name='sampleensemblgeneannotationstats',
            name='sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snpdb.sample'),
        ),
        migrations.AddField(
            model_name='sampleclinvarannotationstatspassingfilter',
            name='clinvar_version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.clinvarversion'),
        ),
        migrations.AddField(
            model_name='sampleclinvarannotationstatspassingfilter',
            name='sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snpdb.sample'),
        ),
        migrations.AddField(
            model_name='sampleclinvarannotationstats',
            name='clinvar_version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.clinvarversion'),
        ),
        migrations.AddField(
            model_name='sampleclinvarannotationstats',
            name='sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snpdb.sample'),
        ),
        migrations.AddField(
            model_name='phenotypemim',
            name='hpo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.humanphenotypeontology'),
        ),
        migrations.AddField(
            model_name='phenotypemim',
            name='mim_morbid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.mimmorbid'),
        ),
        migrations.AddField(
            model_name='patienttextphenotype',
            name='approved_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='patienttextphenotype',
            name='patient',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='patient_text_phenotype', to='patients.patient'),
        ),
        migrations.AddField(
            model_name='patienttextphenotype',
            name='phenotype_description',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='annotation.phenotypedescription'),
        ),
        migrations.AddField(
            model_name='mimmorbidalias',
            name='mim_morbid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.mimmorbid'),
        ),
        migrations.AddField(
            model_name='mimgene',
            name='gene',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='genes.gene'),
        ),
        migrations.AddField(
            model_name='mimgene',
            name='mim_morbid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.mimmorbid'),
        ),
        migrations.AddField(
            model_name='manualvariantentrycollection',
            name='genome_build',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snpdb.genomebuild'),
        ),
        migrations.AddField(
            model_name='manualvariantentrycollection',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='manualvariantentry',
            name='manual_variant_entry_collection',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.manualvariantentrycollection'),
        ),
        migrations.AddField(
            model_name='humanproteinatlasannotation',
            name='gene',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='genes.gene'),
        ),
        migrations.AddField(
            model_name='humanproteinatlasannotation',
            name='tissue_sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.humanproteinatlastissuesample'),
        ),
        migrations.AddField(
            model_name='humanproteinatlasannotation',
            name='version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.humanproteinatlasannotationversion'),
        ),
        migrations.AddField(
            model_name='humanphenotypeontology',
            name='children',
            field=models.ManyToManyField(blank=True, related_name='_parents', through='annotation.HPOEdge', to='annotation.HumanPhenotypeOntology'),
        ),
        migrations.AddField(
            model_name='hposynonym',
            name='hpo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.humanphenotypeontology'),
        ),
        migrations.AddField(
            model_name='hpoedge',
            name='child',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='humanphenotypeontology_parent', to='annotation.humanphenotypeontology'),
        ),
        migrations.AddField(
            model_name='hpoedge',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='humanphenotypeontology_child', to='annotation.humanphenotypeontology'),
        ),
        migrations.AddField(
            model_name='genevaluecountcollection',
            name='gene_count_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.genecounttype'),
        ),
        migrations.AddField(
            model_name='genevaluecountcollection',
            name='source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.variantsource'),
        ),
        migrations.AddField(
            model_name='genevaluecount',
            name='collection',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.genevaluecountcollection'),
        ),
        migrations.AddField(
            model_name='genevaluecount',
            name='gene',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='genes.gene'),
        ),
        migrations.AddField(
            model_name='genevaluecount',
            name='value',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.genevalue'),
        ),
        migrations.AddField(
            model_name='genevalue',
            name='gene_count_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.genecounttype'),
        ),
        migrations.AddField(
            model_name='genesymbolpubmedcount',
            name='gene_symbol',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='genes.genesymbol'),
        ),
        migrations.AddField(
            model_name='genesymbolcitation',
            name='citation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.citation'),
        ),
        migrations.AddField(
            model_name='genesymbolcitation',
            name='gene_symbol',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='genes.genesymbol'),
        ),
        migrations.AddField(
            model_name='genediseasevalidityevidence',
            name='citation',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='annotation.citation'),
        ),
        migrations.AddField(
            model_name='genediseasevalidityevidence',
            name='gene_disease',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.genediseasevalidity'),
        ),
        migrations.AddField(
            model_name='genediseasevalidity',
            name='disease_validity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.diseasevalidity'),
        ),
        migrations.AddField(
            model_name='genediseasevalidity',
            name='gene_symbol',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='genes.genesymbol'),
        ),
        migrations.AddField(
            model_name='genediseasecurator',
            name='cached_web_resource',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='annotation.cachedwebresource'),
        ),
        migrations.AddField(
            model_name='genediseasecurator',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='ensemblgeneannotationversion',
            name='genome_build',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snpdb.genomebuild'),
        ),
        migrations.AddField(
            model_name='ensemblgeneannotation',
            name='gene',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='genes.gene'),
        ),
        migrations.AddField(
            model_name='ensemblgeneannotation',
            name='version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.ensemblgeneannotationversion'),
        ),
        migrations.AddField(
            model_name='diseasevalidity',
            name='gene_disease_curator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.genediseasecurator'),
        ),
        migrations.AddField(
            model_name='diseasevalidity',
            name='hpo_synonym',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='annotation.hposynonym'),
        ),
        migrations.AddField(
            model_name='diseasevalidity',
            name='mim_morbid_alias',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='annotation.mimmorbidalias'),
        ),
        migrations.AddField(
            model_name='diseasevalidity',
            name='mondo',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='annotation.monarchdiseaseontology'),
        ),
        migrations.AddField(
            model_name='createdmanualvariant',
            name='manual_variant_entry',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.manualvariantentry'),
        ),
        migrations.AddField(
            model_name='createdmanualvariant',
            name='variant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snpdb.variant'),
        ),
        migrations.AddField(
            model_name='columnvepfield',
            name='variant_grid_column',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='snpdb.variantgridcolumn'),
        ),
        migrations.AddField(
            model_name='columnvcfinfo',
            name='column',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='snpdb.variantgridcolumn'),
        ),
        migrations.AddField(
            model_name='cohortgenecounts',
            name='cohort',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snpdb.cohort'),
        ),
        migrations.AddField(
            model_name='cohortgenecounts',
            name='gene_count_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.genecounttype'),
        ),
        migrations.AddField(
            model_name='cohortgenecounts',
            name='variant_annotation_version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.variantannotationversion'),
        ),
        migrations.AddField(
            model_name='clinvarversion',
            name='genome_build',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snpdb.genomebuild'),
        ),
        migrations.AddField(
            model_name='clinvarcitation',
            name='citation',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='annotation.citation'),
        ),
        migrations.AddField(
            model_name='clinvarcitation',
            name='clinvar_citations_collection',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.clinvarcitationscollection'),
        ),
        migrations.AddField(
            model_name='clinvar',
            name='variant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snpdb.variant'),
        ),
        migrations.AddField(
            model_name='clinvar',
            name='version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.clinvarversion'),
        ),
        migrations.AlterUniqueTogether(
            name='citation',
            unique_together={('citation_source', 'citation_id')},
        ),
        migrations.AddField(
            model_name='cachedcitation',
            name='citation',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='annotation.citation'),
        ),
        migrations.AddField(
            model_name='annotationversion',
            name='clinvar_version',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='annotation.clinvarversion'),
        ),
        migrations.AddField(
            model_name='annotationversion',
            name='ensembl_gene_annotation_version',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='annotation.ensemblgeneannotationversion'),
        ),
        migrations.AddField(
            model_name='annotationversion',
            name='genome_build',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snpdb.genomebuild'),
        ),
        migrations.AddField(
            model_name='annotationversion',
            name='human_protein_atlas_version',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='annotation.humanproteinatlasannotationversion'),
        ),
        migrations.AddField(
            model_name='annotationversion',
            name='variant_annotation_version',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='annotation.variantannotationversion'),
        ),
        migrations.AddField(
            model_name='annotationrun',
            name='annotation_range_lock',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='annotation.annotationrangelock'),
        ),
        migrations.AddField(
            model_name='annotationrangelock',
            name='max_variant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='max_variant', to='snpdb.variant'),
        ),
        migrations.AddField(
            model_name='annotationrangelock',
            name='min_variant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='min_variant', to='snpdb.variant'),
        ),
        migrations.AddField(
            model_name='annotationrangelock',
            name='version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.variantannotationversion'),
        ),
        migrations.AlterUniqueTogether(
            name='varianttranscriptannotation',
            unique_together={('version', 'variant', 'transcript_version')},
        ),
        migrations.AlterUniqueTogether(
            name='variantgeneoverlap',
            unique_together={('version', 'variant', 'annotation_run', 'gene')},
        ),
        migrations.AddField(
            model_name='variantannotationversiondiff',
            name='version_from',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='version_diff_from', to='annotation.variantannotationversion'),
        ),
        migrations.AddField(
            model_name='variantannotationversiondiff',
            name='version_to',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='version_diff_to', to='annotation.variantannotationversion'),
        ),
        migrations.AlterUniqueTogether(
            name='variantannotation',
            unique_together={('version', 'variant')},
        ),
        migrations.AddField(
            model_name='sampleannotationversionvariantsource',
            name='sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snpdb.sample'),
        ),
        migrations.AddField(
            model_name='sampleannotationversionvariantsource',
            name='variant_annotation_version',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='annotation.variantannotationversion'),
        ),
        migrations.AlterUniqueTogether(
            name='phenotypemim',
            unique_together={('hpo', 'mim_morbid')},
        ),
        migrations.AlterUniqueTogether(
            name='mimgene',
            unique_together={('mim_morbid', 'gene')},
        ),
        migrations.AlterUniqueTogether(
            name='hposynonym',
            unique_together={('hpo', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='genevaluecount',
            unique_together={('collection', 'gene', 'value')},
        ),
        migrations.AlterUniqueTogether(
            name='genevalue',
            unique_together={('gene_count_type', 'label')},
        ),
        migrations.AlterUniqueTogether(
            name='genesymbolcitation',
            unique_together={('gene_symbol', 'citation')},
        ),
        migrations.AddField(
            model_name='ensemblgeneannotationversiondiff',
            name='version_from',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='version_diff_from', to='annotation.ensemblgeneannotationversion'),
        ),
        migrations.AddField(
            model_name='ensemblgeneannotationversiondiff',
            name='version_to',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='version_diff_to', to='annotation.ensemblgeneannotationversion'),
        ),
        migrations.AlterUniqueTogether(
            name='ensemblgeneannotation',
            unique_together={('version', 'gene')},
        ),
        migrations.AlterUniqueTogether(
            name='sampleannotationversionvariantsource',
            unique_together={('sample', 'variant_annotation_version')},
        ),
    ]
