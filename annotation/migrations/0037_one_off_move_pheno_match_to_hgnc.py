# Generated by Django 3.2.4 on 2021-12-23 04:38

from django.db import migrations


def _one_off_move_pheno_match_to_hgnc(apps, schema_editor):
    TextPhenotypeMatch = apps.get_model("annotation", "TextPhenotypeMatch")
    OntologyTerm = apps.get_model("ontology", "OntologyTerm")
    ONTOLOGY_SERVICE_HGNC = "HGNC"

    tpm_genes = TextPhenotypeMatch.objects.filter(gene_symbol__isnull=False)
    if tpm_genes.exists():
        if not OntologyTerm.objects.filter(ontology_service=ONTOLOGY_SERVICE_HGNC).exists():
            raise ValueError("TextPhenotypeMatch w/gene_symbol exists, but no HGNC Ontology which we need to move data")
        matched = 0
        missing_genes = set()
        for tpm in tpm_genes:
            gene_symbol = tpm.gene_symbol.symbol
            if ot := OntologyTerm.objects.filter(ontology_service=ONTOLOGY_SERVICE_HGNC, name=gene_symbol).first():
                matched += 1
                tpm.ontology_term = ot
                tpm.save()
            else:
                missing_genes.add(gene_symbol)
                tpm.delete()

        print(f"Changed {matched} records from gene symbol -> HGNC Ontology")
        if missing_genes:
            print(f"Warning: Could not convert TextPhenotypeMatch gene symbols -> HGNC for: {', '.join(missing_genes)}."
                  "This is not critical, if you want you can edit it and re/match or run 'match_patient_phenotypes'")


class Migration(migrations.Migration):

    dependencies = [
        ('annotation', '0036_auto_20211222_0949'),
    ]

    operations = [
        migrations.RunPython(_one_off_move_pheno_match_to_hgnc),
    ]