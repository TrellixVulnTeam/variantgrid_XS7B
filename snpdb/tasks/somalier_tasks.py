import logging
import os
import shutil
from pathlib import Path
from subprocess import CalledProcessError

from django.conf import settings

import celery
import pandas as pd

from library.django_utils.django_file_utils import get_import_processing_dir
from library.log_utils import log_traceback
from library.utils import execute_cmd
from patients.models_enums import Zygosity
from snpdb.models import VCF, Cohort, Trio, SomalierVCFExtract, SomalierConfig, SomalierAncestryRun, \
    SomalierCohortRelate, SomalierRelate, SomalierTrioRelate, SomalierAncestry, SuperPopulationCode, \
    SomalierSampleExtract, ProcessingStatus
from snpdb.variants_to_vcf import vcf_export_to_file


@celery.task
def somalier_vcf_id(vcf_id: int):
    """ Extract, Ancestry, and Relate (Cohort) """
    vcf = VCF.objects.get(pk=vcf_id)
    SomalierVCFExtract.objects.filter(vcf=vcf).delete()  # Delete any previous
    vcf_extract = SomalierVCFExtract.objects.create(vcf=vcf)
    if not vcf.has_genotype:
        vcf_extract.status = ProcessingStatus.SKIPPED
        vcf_extract.save()
        return

    processing_dir = get_import_processing_dir(vcf_extract.pk, "somalier_vcf_extract")

    try:
        cfg = SomalierConfig()
        vcf_filename = _write_somalier_vcf(cfg, processing_dir, vcf_extract)

        # Extract
        somalier_bin = cfg.get_annotation("command")
        extract_cmd = [somalier_bin, "extract",
                       "--out-dir", vcf_extract.get_somalier_dir(),
                       "--sites", cfg.get_sites(vcf.genome_build),
                       "--fasta", vcf.genome_build.reference_fasta,
                       vcf_filename]
        vcf_extract.execute(extract_cmd)

        _somalier_ancestry(vcf_extract)

        SomalierCohortRelate.objects.filter(cohort=vcf.cohort).delete()  # Delete any previous versions
        relate = SomalierCohortRelate.objects.create(cohort=vcf.cohort, cohort_version=vcf.cohort.version)
        _somalier_relate(relate)
    except CalledProcessError:
        log_traceback()
        logging.info("Somalier failed - carrying on with rest of pipeline")

    if settings.VCF_IMPORT_DELETE_TEMP_FILES_ON_SUCCESS:
        shutil.rmtree(processing_dir)


def _write_somalier_vcf(cfg: SomalierConfig, processing_dir, vcf_extract: SomalierVCFExtract):
    vcf = vcf_extract.vcf
    sites_name = os.path.basename(cfg.get_sites(vcf.genome_build))
    sites_vcf_kwargs = {"name": sites_name, "genome_build": vcf.genome_build}
    try:
        sites_vcf = VCF.objects.get(**sites_vcf_kwargs)
    except VCF.DoesNotExist as dne:
        print(f"Expected single VCF loaded via: {sites_vcf_kwargs}")
        raise dne

    sites_qs = sites_vcf.get_variant_qs()
    exported_vcf_filename = os.path.join(processing_dir, f"vcf_{vcf.pk}.vcf.bgz")
    sample_zygosity_count = vcf_export_to_file(vcf, exported_vcf_filename, original_qs=sites_qs)
    for sample, zy in sample_zygosity_count.items():
        ZYG_LOOKUP = {"ref_count": Zygosity.HOM_REF,
                      "het_count": Zygosity.HET,
                      "hom_count": Zygosity.HOM_ALT,
                      "unk_count": Zygosity.UNKNOWN_ZYGOSITY}
        zyg_kwargs = {k: zy[v] for k, v in ZYG_LOOKUP.items()}
        SomalierSampleExtract.objects.create(vcf_extract=vcf_extract, sample=sample, **zyg_kwargs)

    tabix_command = ["tabix", exported_vcf_filename]
    return_code, stdout, stderr = execute_cmd(tabix_command)
    print(f"return_code: {return_code}, stdout: {stdout}, stderr: {stderr}")
    return exported_vcf_filename


def _somalier_ancestry(vcf_extract: SomalierVCFExtract):
    cfg = SomalierConfig()
    ancestry_run = SomalierAncestryRun.objects.create(vcf_extract=vcf_extract)
    compare_samples = os.path.join(cfg.get_annotation("ancestry_somalier_dir"), "*.somalier")
    ancestry_report_dir = Path(ancestry_run.get_report_dir())
    ancestry_report_dir.mkdir(parents=True, exist_ok=True)
    somalier_bin = cfg.get_annotation("command")
    ancestry_cmd = [somalier_bin, "ancestry", "--labels", cfg.get_annotation("ancestry_labels"),
                    compare_samples, "++"] + ancestry_run.get_sample_somalier_filenames()
    ancestry_run.execute(ancestry_cmd, cwd=ancestry_report_dir)

    # Use TSV to write sample specific files
    df = pd.read_csv(ancestry_report_dir / "somalier-ancestry.somalier-ancestry.tsv", sep='\t', index_col=0)
    for sample_extract in vcf_extract.somaliersampleextract_set.all():
        row = df.loc[sample_extract.sample.vcf_sample_name]
        predicted_ancestry = getattr(SuperPopulationCode, row["predicted_ancestry"])  # Get enum ie 'EAS'
        SomalierAncestry.objects.create(ancestry_run=ancestry_run,
                                        sample_extract=sample_extract,
                                        predicted_ancestry=predicted_ancestry,
                                        EAS_prob=row["EAS_prob"],
                                        AFR_prob=row["AFR_prob"],
                                        AMR_prob=row["AMR_prob"],
                                        SAS_prob=row["SAS_prob"],
                                        EUR_prob=row["EUR_prob"])


def _somalier_relate(somalier_relate: SomalierRelate):
    cfg = SomalierConfig()
    somalier_bin = cfg.get_annotation("command")
    processing_dir = get_import_processing_dir(somalier_relate.pk, "somalier_relate")

    ped_filename = os.path.join(processing_dir, "temp.ped")
    somalier_relate.write_ped_file(ped_filename)
    somalier_relate_dir = Path(cfg.related_dir(somalier_relate.uuid))
    somalier_relate_dir.mkdir(parents=True, exist_ok=True)

    command = [somalier_bin, "relate", "--ped", ped_filename] + somalier_relate.get_sample_somalier_filenames()
    somalier_relate.execute(command, cwd=somalier_relate_dir)

    shutil.rmtree(processing_dir)


@celery.task
def somalier_cohort_relate(cohort_id: int):
    cohort = Cohort.objects.get(pk=cohort_id)
    relate = SomalierCohortRelate.objects.create(cohort=cohort, cohort_version=cohort.version)
    _somalier_relate(relate)


@celery.task
def somalier_trio_relate(trio_id: int):
    trio = Trio.objects.get(pk=trio_id)
    relate = SomalierTrioRelate.objects.create(trio=trio)
    _somalier_relate(relate)


# TODO: Do for Pedigree
