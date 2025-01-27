# Generated by Django 3.1.3 on 2021-01-21 06:46

from django.db import migrations

from manual.operations.manual_operations import ManualOperation


def _test_patients_but_no_ontology(apps):
    # If we have patients but no ontology - need to do rematching
    OntologyTerm = apps.get_model("ontology", "OntologyTerm")
    PatientTextPhenotype = apps.get_model("annotation", "PatientTextPhenotype")
    return PatientTextPhenotype.objects.exists() and not OntologyTerm.objects.exists()


def _one_off_move_ontology(apps, schema_editor):
    TextPhenotypeMatch = apps.get_model("annotation", "TextPhenotypeMatch")
    OntologyTerm = apps.get_model("ontology", "OntologyTerm")

    if not OntologyTerm.objects.exists():
        return  # Don't do anything, just re-match using management command

    for tpm in TextPhenotypeMatch.objects.filter(hpo__isnull=False):
        hpo_id = "HP:%07d" % int(tpm.hpo_id)
        tpm.ontology_term = OntologyTerm.objects.get(pk=hpo_id)
        tpm.save()

    MOVED_OMIM = {
        614087: 227650,  # Fancomi anaemia
    }

    for tpm in TextPhenotypeMatch.objects.filter(omim_alias__isnull=False):
        mim_id = int(tpm.omim_alias.mim_morbid_id)
        mim_id = MOVED_OMIM.get(mim_id, mim_id)  # Some have been replaced
        omim_id = "OMIM:%d" % mim_id
        try:
            tpm.ontology_term = OntologyTerm.objects.get(pk=omim_id)
        except OntologyTerm.DoesNotExist:
            # If an OMIM term is gone but also matched to a gene, don't worry about it
            if gene_tpm := TextPhenotypeMatch.objects.filter(text_phenotype=tpm.text_phenotype,
                                                             offset_start=tpm.offset_start,
                                                             offset_end=tpm.offset_end,
                                                             match_type='G').first():
                print(f"No OMIM term: {omim_id} but ok as matched to gene: {gene_tpm.gene_symbol}")
                continue
            print(f"Could not load: {omim_id}")
            raise

        tpm.save()


class Migration(migrations.Migration):

    dependencies = [
        ('annotation', '0015_textphenotypematch_ontology_term'),
    ]

    operations = [
        ManualOperation(task_id=ManualOperation.task_id_manage(["match_patient_phenotypes", "--clear"]),
                        test=_test_patients_but_no_ontology),
        migrations.RunPython(_one_off_move_ontology)
    ]
