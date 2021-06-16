# Generated by Django 3.1.6 on 2021-06-02 04:38

from django.db import migrations

from classification.autopopulate_evidence_keys.clinvar_option_updator import ClinVarOptionUpdator


def clinical_significance(apps, schema_editor):
    options = ClinVarOptionUpdator(apps, "clinical_significance")
    options.set_clinvar_option("B", "Benign")
    options.set_clinvar_option("LB", "Likely benign")
    options.set_clinvar_option("VUS", "Uncertain significance")
    options.set_clinvar_option("VUS_A", "Uncertain significance")
    options.set_clinvar_option("VUS_B", "Uncertain significance")
    options.set_clinvar_option("VUS_C", "Uncertain significance")
    options.set_clinvar_option("LP", "Likely pathogenic")
    options.set_clinvar_option("P", "Pathogenic")
    options.set_clinvar_option("D", "drug response")
    options.set_clinvar_option("R", "risk factor")

"""
*variantgrid
digenic_recessive : Digenic recessive
digenic_dominant : Digenic dominant
isolated_cases : Isolated cases
imprinting : Imprinting

*clinvar
"Genetic anticipation",
"Sporadic",
"Codominant",
"Autosomal dominant inheritance with maternal imprinting",
"Autosomal dominant inheritance with paternal imprinting",
"Multifactorial inheritance",
"""

def mode_of_inheritance(apps, schema_editor):
    options = ClinVarOptionUpdator(apps, "mode_of_inheritance")
    options.set_clinvar_option("autosomal_dominant", "Autosomal dominant inheritance")
    options.set_clinvar_option("autosomal_recessive", "Autosomal recessive inheritance")
    options.set_clinvar_option("autosomal_unknown", "Autosomal unknown")

    options.set_clinvar_option("sex_limited_autosomal_dominant", "Sex-limited autosomal dominant")

    options.set_clinvar_option("mitochondrial", "Mitochondrial inheritance")
    options.set_clinvar_option("x_linked", "X-linked inheritance")
    options.set_clinvar_option("x_linked_recessive", "X-linked recessive inheritance")
    options.set_clinvar_option("x_linked_dominant", "X-linked dominant inheritance")
    options.set_clinvar_option("y_linked", "Y-linked inheritance")

    options.set_clinvar_option("somatic", "Somatic mutation")
    options.set_clinvar_option("oligogenic", "Oligogenic inheritance")

    options.set_clinvar_option("other", "Other")
    options.set_clinvar_option("unknown", "Unknown mechanism")
    options.set_clinvar_option("multifactorial", "Multifactorial")


def allele_origin(apps, schema_editor):
    options = ClinVarOptionUpdator(apps, "allele_origin")
    options.set_clinvar_option("germline", "germline")
    options.set_clinvar_option("somatic", "somatic")
    options.set_clinvar_option("unknown", "unknown")
    options.set_clinvar_option("tested_inconclusive", "Tested inconclusive")

"""
*variantgrid
likely_germline : Likely germline
likely_somatic : Likely somatic
not_tested : Not tested
other : Other

*clinvar
"de novo",
"not provided",
"inherited",
"maternal",
"paternal",
"biparental",
"not-reported",
"not applicable",
"experimentally generated"
"""

class Migration(migrations.Migration):

    dependencies = [
        ('classification', '0029_update_ekey_molecular_consequence'),
    ]

    operations = [
        migrations.RunPython(clinical_significance),
        migrations.RunPython(mode_of_inheritance),
        migrations.RunPython(allele_origin)
    ]