# Generated by Django 4.0.3 on 2022-05-16 06:40

from django.db import migrations

from library.django_utils import bulk_insert_class_data


def _new_vep_columns(apps, schema_editor):
    VARIANT_GRID_COLUMN = [
        {'grid_column_name': 'nmd_escaping_variant',
         'variant_column': 'variantannotation__nmd_escaping_variant',
         'annotation_level': 'T',
         'width': None,
         'label': 'NMD escaping',
         'description': 'Predicts if a stop_gained variant could escape NMD. True if any of the following are met: 1. Variant is in last exon 2. Variant is less than 50 bases upstream of the penultimate (second to the last ) exon. 3. Variant falls in the first 100 coding bases. 4. Transcript has only 1 exon (no introns)',
         'model_field': True,
         'queryset_field': True},

        # dbNSFP
        {'grid_column_name': 'cadd_raw_rankscore',
         'variant_column': 'variantannotation__cadd_raw_rankscore',
         'annotation_level': 'V',
         'width': None,
         'label': 'CADD raw rankscore',
         'description': '<a href="https://doi.org/10.1093/nar/gky1016">CADD</a> score. Rankscore (0-1) of all non-synonymous SNVs',
         'model_field': True,
         'queryset_field': True},
        {'grid_column_name': 'revel_rankscore',
         'variant_column': 'variantannotation__revel_rankscore',
         'annotation_level': 'V',
         'width': None,
         'label': 'REVEL rankscore',
         'description': '<a href="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5065685/">REVEL</a> is an ensemble score based on 13 individual scores. Rankscore (0-1) of all non-synonymous SNVs',
         'model_field': True,
         'queryset_field': True},
        {'grid_column_name': 'bayesdel_noaf_rankscore',
         'variant_column': 'variantannotation__bayesdel_noaf_rankscore',
         'annotation_level': 'V',
         'width': None,
         'label': 'BayesDel noAF rankscore',
         'description': 'Deleteriousness prediction meta-score for SNVs and indels without inclusion of MaxAF. <a href="https://doi.org/10.1002/humu.23158">see paper</a> Rankscore (0-1) of all non-synonymous SNVs',
         'model_field': True,
         'queryset_field': True},
        {'grid_column_name': 'clinpred_rankscore',
         'variant_column': 'variantannotation__clinpred_rankscore',
         'annotation_level': 'V',
         'width': None,
         'label': 'ClinPred rankscore',
         'description': 'A deleteriousness prediction meta-score, <a href="https://doi.org/10.1016/j.ajhg.2018.08.005">see paper</a> Rankscore (0-1) of all non-synonymous SNVs',
         'model_field': True,
         'queryset_field': True},
        {'grid_column_name': 'vest4_rankscore',
         'variant_column': 'variantannotation__vest4_rankscore',
         'annotation_level': 'V',
         'width': None,
         'label': 'VEST4 rankscore',
         'description': '<a href="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3665549/">VEST</a> version 4. Rankscore (0-1) of all non-synonymous SNVs',
         'model_field': True,
         'queryset_field': True},
        {'grid_column_name': 'metalr_rankscore',
         'variant_column': 'variantannotation__metalr_rankscore',
         'annotation_level': 'V',
         'width': None,
         'label': 'MetaLR rankscore',
         'description': 'Meta score of 10 component scores (SIFT, PolyPhen-2 HDIV, PolyPhen-2 HVAR, GERP++, MutationTaster, Mutation Assessor, FATHMM, LRT, SiPhy, PhyloP) and the maximum frequency observed in the 1000 genomes populations. <a href="https://academic.oup.com/hmg/article/24/8/2125/651446"></a>. Rankscore (0-1) of all non-synonymous SNVs',
         'model_field': True,
         'queryset_field': True},
        # ALoFT
        {'grid_column_name': 'aloft_prob_tolerant',
         'variant_column': 'variantannotation__aloft_prob_tolerant',
         'annotation_level': 'V',
         'width': None,
         'label': 'ALoFT Prob Tol',
         'description': '<a href="https://www.nature.com/articles/s41467-017-00443-5">ALoFT</a> probability of being classified benign.',
         'model_field': True,
         'queryset_field': True},
        {'grid_column_name': 'aloft_prob_recessive',
         'variant_column': 'variantannotation__aloft_prob_recessive',
         'annotation_level': 'V',
         'width': None,
         'label': 'ALoFT Prob Rec',
         'description': '<a href="https://www.nature.com/articles/s41467-017-00443-5">ALoFT</a> probability of being classified as recessive disease causing',
         'model_field': True,
         'queryset_field': True},
        {'grid_column_name': 'aloft_prob_dominant',
         'variant_column': 'variantannotation__aloft_prob_dominant',
         'annotation_level': 'V',
         'width': None,
         'label': 'ALoFT Prob Dom',
         'description': '<a href="https://www.nature.com/articles/s41467-017-00443-5">ALoFT</a> probability of being classified as dominant disease causing',
         'model_field': True,
         'queryset_field': True},
        {'grid_column_name': 'aloft_pred',
         'variant_column': 'variantannotation__aloft_pred',
         'annotation_level': 'V',
         'width': None,
         'label': 'ALoFT Pred',
         'description': '<a href="https://www.nature.com/articles/s41467-017-00443-5">ALoFT</a> final classification, values can be Tolerant, Recessive or Dominant',
         'model_field': True,
         'queryset_field': True},
        {'grid_column_name': 'aloft_high_confidence',
         'variant_column': 'variantannotation__aloft_high_confidence',
         'annotation_level': 'V',
         'width': None,
         'label': 'ALoFT high confidence',
         'description': '<a href="https://www.nature.com/articles/s41467-017-00443-5">ALoFT</a> Confidence level of Aloft_pred is "High Confidence" (p < 0.05)',
         'model_field': True,
         'queryset_field': True},
        {'grid_column_name': 'aloft_ensembl_transcript',
         'variant_column': 'variantannotation__aloft_ensembl_transcript',
         'annotation_level': 'V',
         'width': None,
         'label': 'ALoFT chosen transcript',
         'description': '<a href="https://www.nature.com/articles/s41467-017-00443-5">ALoFT</a> Ensembl transcript of most damaging prediction chosen.',
         'model_field': True,
         'queryset_field': True},
    ]

    bulk_insert_class_data(apps, "snpdb", [("VariantGridColumn", VARIANT_GRID_COLUMN)])


def _reverse_new_vep_columns(apps, schema_editor):
    VariantGridColumn = apps.get_model("snpdb", "VariantGridColumn")
    NEW_COLUMNS = ['nmd_escaping_variant', 'cadd_raw_rankscore', 'revel_rankscore', 'bayesdel_noaf_rankscore',
                   'clinpred_rankscore', 'vest4_rankscore', 'metalr_rankscore', 'aloft_prob_tolerant',
                   'aloft_prob_recessive', 'aloft_prob_dominant', 'aloft_pred', 'aloft_high_confidence']

    VariantGridColumn.objects.filter(grid_column_name__in=NEW_COLUMNS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('snpdb', '0072_variant_wiki_column'),
    ]

    operations = [
        migrations.RunPython(_new_vep_columns, reverse_code=_reverse_new_vep_columns),
    ]