# Generated by Django 3.1.3 on 2021-01-21 06:46

from django.db import migrations
import pandas as pd

from library.file_utils import mk_path
from manual.operations.manual_operations import ManualOperation


def _test_has_legacy_phenotype_node_ontology(apps):
    PhenotypeNodeOMIM = apps.get_model("analysis", "PhenotypeNodeOMIM")
    PhenotypeNodeHPO = apps.get_model("analysis", "PhenotypeNodeHPO")
    return PhenotypeNodeOMIM.objects.exists() or PhenotypeNodeHPO.objects.exists()


def _one_off_save_phenotype_node_ontology(apps, schema_editor):
    PhenotypeNodeOMIM = apps.get_model("analysis", "PhenotypeNodeOMIM")
    PhenotypeNodeHPO = apps.get_model("analysis", "PhenotypeNodeHPO")

    mk_path("data/migrations")
    if PhenotypeNodeHPO.objects.exists():
        hpo_data = PhenotypeNodeHPO.objects.all().values("phenotype_node", "hpo_synonym__hpo")
        df = pd.DataFrame.from_records(hpo_data)
        hpo_filename = "data/migrations/hpo_legacy.csv"
        print(f"Saved legacy phenotype node data to {hpo_filename}")
        df.to_csv(hpo_filename)
        PhenotypeNodeHPO.objects.all().delete()

    if PhenotypeNodeOMIM.objects.exists():
        omim_data = PhenotypeNodeOMIM.objects.all().values("phenotype_node", "mim_morbid_alias__mim_morbid")
        df = pd.DataFrame.from_records(omim_data)
        omim_filename = "data/migrations/omim_legacy.csv"
        print(f"Saved legacy phenotype node data to {omim_filename}")
        df.to_csv(omim_filename)
        PhenotypeNodeOMIM.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0013_phenotypenodeontologyterm'),
    ]

    operations = [
        ManualOperation(task_id=ManualOperation.task_id_manage(["fix_legacy_phenotype_nodes"]),
                        test=_test_has_legacy_phenotype_node_ontology),
        migrations.RunPython(_one_off_save_phenotype_node_ontology)
    ]
