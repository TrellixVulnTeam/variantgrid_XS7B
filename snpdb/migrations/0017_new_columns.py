# Generated by Django 3.1 on 2021-02-02 04:15

from django.db import migrations

from library.django_utils import bulk_insert_class_data


def new_columns(apps, schema_editor):
    VariantGridColumn = apps.get_model("snpdb", "VariantGridColumn")
    CustomColumn = apps.get_model("snpdb", "CustomColumn")

    HGNC_LEVEL = 'H'
    UNIPROT_LEVEL = 'U'

    MODIFY_COLUMNS = {
        "band": {"variant_column": "variantannotation__transcript_version__gene_version__hgnc__location", "annotation_level": HGNC_LEVEL},
        "ccds_ids": {"variant_column": "variantannotation__transcript_version__gene_version__hgnc__ccds_ids", "annotation_level": HGNC_LEVEL},
        "function_from_uniprotkb": {"variant_column": "variantannotation__uniprot__function", "annotation_level": UNIPROT_LEVEL},
        "gene_family_description": {"variant_column": "variantannotation__transcript_version__gene_version__hgnc__gene_groups", "annotation_level": HGNC_LEVEL},
        "gene_family_tag": {"variant_column": "variantannotation__transcript_version__gene_version__hgnc__gene_group_ids", "annotation_level": HGNC_LEVEL},
        "hgnc_name": {"variant_column": "variantannotation__transcript_version__gene_version__hgnc__approved_name", "annotation_level": HGNC_LEVEL},
        "hgnc_symbol": {"variant_column": "variantannotation__transcript_version__gene_version__hgnc__gene_symbol", "annotation_level": HGNC_LEVEL},
        "mgi_id": {"variant_column": "variantannotation__transcript_version__gene_version__hgnc__mgd_ids", "annotation_level": HGNC_LEVEL},
        "omim_id": {"variant_column": "variantannotation__transcript_version__gene_version__hgnc__omim_ids", "annotation_level": HGNC_LEVEL},
        "pathway_from_uniprotkb": {"variant_column": "variantannotation__uniprot__pathway", "annotation_level": UNIPROT_LEVEL},
        "previous_symbols": {"variant_column": "variantannotation__transcript_version__gene_version__hgnc__previous_symbols", "annotation_level": HGNC_LEVEL},
        "refseq_gene_summary": {"variant_column": "variantannotation__gene__summary"},
        "rgd_id": {"variant_column": "variantannotation__transcript_version__gene_version__hgnc__rgd_ids", "annotation_level": HGNC_LEVEL},
        "rvis_percentile": {"variant_column": "variantannotation__gene__geneannotation__rvis_oe_ratio_percentile"},
        "synonyms": {"variant_column": "variantannotation__transcript_version__gene_version__hgnc__alias_symbols", "annotation_level": HGNC_LEVEL},
        "tissue_specificity_from_uniprotkb": {"variant_column": "variantannotation__uniprot__tissue_specificity", "annotation_level": UNIPROT_LEVEL},
        "ucsc_id": {"variant_column": "variantannotation__transcript_version__gene_version__hgnc__ucsc_ids", "annotation_level": HGNC_LEVEL},
        "uniprot_id": {"variant_column": "variantannotation__uniprot_id"},
    }

    NEW_VARIANT_GRID_COLUMNS = [
        {'grid_column_name': 'gene_biotype',
         'variant_column': 'variantannotation__transcript_version__gene_version__biotype',
         'annotation_level': 'G',
         'width': None,
         'label': 'Gene Biotype',
         'description': "Gene Biotypes from RefSeq or <a href='http://asia.ensembl.org/info/genome/genebuild/biotypes.html'>Ensembl</a> annotation",
         'model_field': True,
         'queryset_field': True},
        {'grid_column_name': 'gnomad_oe_lof',
         'variant_column': 'variantannotation__gene__geneannotation__gnomad_oe_lof',
         'annotation_level': 'G',
         'width': None,
         'label': 'gnomAD OE LOF',
         'description': 'Loss Of Function (OE) scores, see <a href="https://gnomad.broadinstitute.org/faq#constraint">gnomAD FAQ</a> ',
         'model_field': True,
         'queryset_field': True},
        {'grid_column_name': 'hpo_terms',
         'variant_column': 'variantannotation__gene__geneannotation__hpo_terms',
         'annotation_level': 'G',
         'width': None,
         'label': 'HPO terms',
         'description': 'Human Phenotype Ontology terms associated with gene, joined with " | "',
         'model_field': True,
         'queryset_field': True},
        {'grid_column_name': 'omim_terms',
         'variant_column': 'variantannotation__gene__geneannotation__omim_terms',
         'annotation_level': 'G',
         'width': None,
         'label': 'OMIM terms',
         'description': 'Online Mendelian Inheritance in Man terms associated with gene, joined with " | "',
         'model_field': True,
         'queryset_field': True},
        {'grid_column_name': 'uniprot_reactome',
         'variant_column': 'variantannotation__uniprot__reactome',
         'annotation_level': 'U',
         'width': None,
         'label': 'UniProt reactome',
         'description': "From <a target='_blank', href='http://www.uniprot.org/'>Universal Protein Knowledgebase</a>",
         'model_field': True,
         'queryset_field': True},
    ]

    NEW_COLUMN_VCF_INFO = [
        {'info_id': 'GENE_BIOTYPE', 'column_id': 'gene_biotype', 'number': None, 'type': 'S',
         'description': 'Gene Biotype'},
        {'info_id': 'GNOMAD_GENE_OE_LOF', 'column_id': 'gnomad_oe_lof', 'number': None, 'type': 'F',
         'description': 'gnomAD Gene Constraint LoF (OE)'},
        {'info_id': 'HPO_TERMS', 'column_id': 'hpo_terms', 'number': None, 'type': 'S',
         'description': 'Human Phenotype Ontology terms associated with gene'},
        {'info_id': 'OMIM_TERMS', 'column_id': 'omim_terms', 'number': None, 'type': 'S',
         'description': 'Online Mendelian Inheritance in Man terms associated with gene'},
        {'info_id': 'UNIPROT_REACTOME', 'column_id': 'uniprot_reactome', 'number': None, 'type': 'S',
         'description': 'UniProt reactome'},
    ]

    # old: new
    REPLACED_COLUMNS = {
        "omim_phenotypes": "omim_terms",
        "phenotypes_from_ensembl": "hpo_terms",
    }

    DELETE_COLUMNS = [
        "end_position",
        "entrez_gene_id",
        "enzyme_ids",
        "external_gene_name",
        "hgnc_symbol_lower",
        "in_cancer_gene_census",
        "percentage_gc_content",
        "start_position",
        "status",
        "strand",
        "transcript_count",
    ]

    bulk_insert_class_data(apps, "snpdb", [("VariantGridColumn", NEW_VARIANT_GRID_COLUMNS)])
    bulk_insert_class_data(apps, "snpdb", [("ColumnVCFInfo", NEW_COLUMN_VCF_INFO)])

    for pk, data in MODIFY_COLUMNS.items():
        VariantGridColumn.objects.filter(pk=pk).update(**data)

    for old_column, new_column in REPLACED_COLUMNS.items():
        CustomColumn.objects.filter(column_id=old_column).update(column_id=new_column)

    VariantGridColumn.objects.filter(pk__in=REPLACED_COLUMNS).delete()
    VariantGridColumn.objects.filter(pk__in=DELETE_COLUMNS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('snpdb', '0016_auto_20210202_1444'),
    ]

    operations = [
        migrations.RunPython(new_columns)
    ]
