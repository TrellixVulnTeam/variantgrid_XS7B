# Generated by Django 4.0.6 on 2022-07-28 02:18

from django.db import migrations


def _one_off_gene_annotation_assign_ontology_version(apps, schema_editor):
    GeneAnnotationVersion = apps.get_model("annotation", "GeneAnnotationVersion")
    OntologyVersion = apps.get_model("ontology", "OntologyVersion")

    legacy = OntologyVersion.objects.order_by("pk").first()
    for gav in GeneAnnotationVersion.objects.all():
        last_ontology_import_id = gav.last_ontology_import_id
        older_ov_qs = OntologyVersion.objects.filter(gencc_import_id__lte=last_ontology_import_id,
                                                     mondo_import__lte=last_ontology_import_id,
                                                     hp_owl_import_id__lte=last_ontology_import_id,
                                                     hp_phenotype_to_genes_import_id__lte=last_ontology_import_id)
        if ov := older_ov_qs.order_by("pk").last():
            print(f"Assigning GeneAnnotationVersion {gav.pk} OntologyVersion {ov.pk} ")
        else:
            print("Warning: Could not find OntologyVersion for GeneAnnotationVersion pk={gav.pk}" \
                  f" with ontology versions <= {last_ontology_import_id=}. Using legacy OntologyVersion ({legacy.pk})")
            ov = legacy
        if ov:
            gav.ontology_version = ov
            gav.save()


class Migration(migrations.Migration):

    dependencies = [
        ('annotation', '0057_geneannotationversion_ontology_version'),
        ('ontology', '0017_alter_ontologyimport_version_and_more'),
    ]

    operations = [
        migrations.RunPython(_one_off_gene_annotation_assign_ontology_version),
    ]
