# Generated by Django 4.0.3 on 2022-04-26 02:27

from django.db import migrations


def _one_off_migrate_human_protein_atlas(apps, schema_editor):
    """
        HPA v15 used abundances + scores (FPKM) but we only imported abundances
        Later versions only have scores (nTPM) so we'll put back scores that will keep the historical filters
        the same (if you actually want exact scores, just re-import v15 again)
    """
    HumanProteinAtlasAnnotationVersion = apps.get_model("annotation", "HumanProteinAtlasAnnotationVersion")
    HumanProteinAtlasAnnotation = apps.get_model("annotation", "HumanProteinAtlasAnnotation")

    hpa_version = HumanProteinAtlasAnnotationVersion.objects.filter(hpa_version=15).first()
    if hpa_version is None:
        return

    NOT_DETECTED = 'N'
    LOW = 'L'
    MEDIUM = 'M'
    HIGH = 'H'

    ABUNDANCE_MINS = {
        NOT_DETECTED: 0.0,
        LOW: 0.5,
        MEDIUM: 10,
        HIGH: 50,
    }

    for abundance, value_min in ABUNDANCE_MINS.items():
        HumanProteinAtlasAnnotation.objects.filter(version=hpa_version, abundance=abundance).update(value=value_min)



class Migration(migrations.Migration):

    dependencies = [
        ('annotation', '0045_humanproteinatlasannotation_gene_symbol_and_more'),
    ]

    operations = [
        migrations.RunPython(_one_off_migrate_human_protein_atlas),
    ]
