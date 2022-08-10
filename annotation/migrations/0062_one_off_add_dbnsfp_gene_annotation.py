# Generated by Django 4.0.6 on 2022-08-08 07:45
from django.conf import settings
from django.db import migrations

from manual.operations.manual_operations import ManualOperation


def _test_needs_gene_annotation_update(apps):
    """ Only if deployment needs it, and has existing gene annotations missing dbNSFP gene annotation """

    if settings.ANNOTATION_GENE_ANNOTATION_VERSION_ENABLED:
        GeneAnnotationVersion = apps.get_model("annotation", "GeneAnnotationVersion")
        return GeneAnnotationVersion.objects.filter(dbnsfp_gene_version__isnull=True).exists()
    return False


def _test_existing_deploy_without_dbnsfp(apps):
    """ Only for existing systems, ie not fresh / test """
    AnnotationVersion = apps.get_model("annotation", "AnnotationVersion")
    DBNSFPGeneAnnotationVersion = apps.get_model("annotation", "DBNSFPGeneAnnotationVersion")
    return AnnotationVersion.objects.all().exists() and not DBNSFPGeneAnnotationVersion.objects.all().exists()


def _one_off_remove_loftool_vep(apps, schema_editor):
    ColumnVEPField = apps.get_model("annotation", "ColumnVEPField")
    ColumnVEPField.objects.filter(variant_grid_column='loftool').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('annotation', '0061_dbnsfpgeneannotationversion_and_more'),
    ]

    operations = [
        ManualOperation.operation_other(args=["Import dbNSFP gene annotation (see annotation page)"],
                                        test=_test_existing_deploy_without_dbnsfp),
        # Only need this if using gene annotation
        ManualOperation(task_id=ManualOperation.task_id_manage(["gene_annotation", "--add-dbnsfp-gene"]),
                        test=_test_needs_gene_annotation_update),
        migrations.RunPython(_one_off_remove_loftool_vep, reverse_code=lambda apps, schema_editor: None),
    ]
