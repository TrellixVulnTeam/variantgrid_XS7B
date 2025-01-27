# Generated by Django 3.1 on 2021-05-05 05:46

from django.db import migrations
from django.db.models import F
from django.db.models.functions import Upper


def _one_off_fix_lowercase_gene_symbols(apps, schema_editor):
    GeneSymbol = apps.get_model("genes", "GeneSymbol")

    # Create upper case versions of symbols that don't exist
    lc_symbols_qs = GeneSymbol.objects.annotate(uc_symbol=Upper("symbol")).exclude(symbol=F("uc_symbol"))
    lc_symbols = list(lc_symbols_qs.values_list("uc_symbol", flat=True))
    GeneSymbol.objects.bulk_create([GeneSymbol(symbol=s.upper()) for s in lc_symbols],
                                   batch_size=2000, ignore_conflicts=True)

    # 'annotation.GeneSymbolPubMedCount' is 1-to-1 with gene symbol, but is just a cache so can delete ok
    GeneSymbolPubMedCount = apps.get_model("annotation", "GeneSymbolPubMedCount")
    GeneSymbolPubMedCount.objects.filter(gene_symbol__in=lc_symbols_qs).delete()

    # ReleaseGeneSymbol has a unique_together with gene_symbol - so need to delete any lower symbols
    # That already have upper symbols
    GeneAnnotationRelease = apps.get_model("genes", "GeneAnnotationRelease")
    ReleaseGeneSymbol = apps.get_model("genes", "ReleaseGeneSymbol")

    for gar in GeneAnnotationRelease.objects.all():
        qs = ReleaseGeneSymbol.objects.filter(release=gar).annotate(uc_gene_symbol=Upper("gene_symbol"))
        upper_symbols = qs.filter(gene_symbol=F("uc_gene_symbol")).values_list("gene_symbol", flat=True)
        lower_symbols = qs.exclude(gene_symbol=F("uc_gene_symbol"))
        lower_with_existing_upper = lower_symbols.filter(uc_gene_symbol__in=upper_symbols)
        count = lower_with_existing_upper.delete()
        print(f"Deleted {count} lowercase copies of UPPER for {gar}")

        # TODO: Also need to handle
        # ReleaseGeneSymbolGene

    # All the aliases were upper case - no need to do that.
    MODELS = [
        ("analysis", "AllVariantsNode"),
        ("annotation", "GeneDiseaseValidity"),
        ("annotation", "GeneSymbolCitation"),
        ("annotation", "TextPhenotypeMatch"),
        ("classification", "ClinVarExport"),
        ("classification", "ConditionTextMatch"),
        ("genes", "GeneSymbolAlias"),
        ("genes", "GeneVersion"),
        ("genes", "GeneListGeneSymbol"),
        ("genes", "CanonicalTranscript"),
        ("genes", "GeneCoverage"),
        ("genes", "GeneCoverageCanonicalTranscript"),
        ("genes", "GnomADGeneConstraint"),
        ("genes", "HGNC"),
        ("genes", "ReleaseGeneSymbol"),  # Should work now we cleaned upper/lower dupes above
        ("pathtests", "PathologyTestGeneModificationRequest"),
        ("seqauto", "GoldCoverageSummary"),
    ]

    for app_label, model_name in MODELS:
        klass = apps.get_model(app_label, model_name)
        qs = klass.objects.annotate(uc_gene_symbol=Upper("gene_symbol")).exclude(gene_symbol=F("uc_gene_symbol"))
        count = qs.update(gene_symbol=F("uc_gene_symbol"))
        print(f"{model_name}: changed {count} lowercase gene_symbol->GENE_SYMBOL")

    count, classes = lc_symbols_qs.delete()
    other_classes = set(classes) - {'genes.GeneSymbol'}
    if other_classes:
        msg = f"Something unexpected would have been deleted by deleting lowercase gene symbols: {other_classes}"
        raise ValueError(msg)


class Migration(migrations.Migration):

    dependencies = [
        ('classification', '0015_auto_20210108_1435'),
        ('genes', '0027_one_off_fix_panel_app_gene_list_permissions'),
    ]

    operations = [
        migrations.RunPython(_one_off_fix_lowercase_gene_symbols)
    ]
