"""
Liftover via Clingen Allele Registry or NCBI remap
"""
from collections import defaultdict
from typing import Dict, List, Tuple, Any

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from functools import reduce
import operator
import os

from library.django_utils.django_file_utils import get_import_processing_dir
from library.log_utils import log_traceback
from library.vcf_utils import write_vcf_from_tuples
from snpdb.models.models_genome import GenomeBuild, Contig, GenomeFasta
from snpdb.models.models_variant import AlleleSource, Liftover, Allele, Variant
from snpdb.models.models_enums import ImportSource, AlleleConversionTool
from upload.models import UploadedFile, UploadedLiftover, UploadPipeline
from upload.models_enums import UploadedFileTypes
from upload.upload_processing import process_upload_pipeline


def create_liftover_pipelines(user: User, allele_source: AlleleSource,
                              import_source: ImportSource,
                              inserted_genome_build: GenomeBuild = None):
    """ Creates and runs a liftover pipeline for each destination GenomeBuild """

    build_liftover_vcf_tuples = _get_build_liftover_vcf_tuples(allele_source, inserted_genome_build)
    for genome_build, liftover_vcf_tuples in build_liftover_vcf_tuples.items():
        for conversion_tool, vcf_tuples in liftover_vcf_tuples.items():
            liftover = Liftover.objects.create(user=user,
                                               allele_source=allele_source,
                                               conversion_tool=conversion_tool,
                                               genome_build=genome_build)

            # Because we need to normalise / insert etc, it's easier just to write a VCF
            # and run through upload pipeline
            working_dir = get_import_processing_dir(liftover.pk, "liftover")
            liftover_vcf_filename = os.path.join(working_dir, f"liftover_variants.{genome_build.name}.vcf")
            if AlleleConversionTool.vcf_tuples_in_destination_build(conversion_tool):
                vcf_filename = liftover_vcf_filename  # Can write directly
            else:
                vcf_filename = os.path.join(working_dir, f"source_variants.{inserted_genome_build.name}.vcf")
                liftover.source_vcf = vcf_filename
                liftover.source_genome_build = inserted_genome_build
                liftover.save()

            write_vcf_from_tuples(vcf_filename, vcf_tuples, tuples_have_id_field=True)
            uploaded_file = UploadedFile.objects.create(path=liftover_vcf_filename,
                                                        import_source=import_source,
                                                        name='Liftover',
                                                        user=user,
                                                        file_type=UploadedFileTypes.LIFTOVER,
                                                        visible=False)

            UploadedLiftover.objects.create(uploaded_file=uploaded_file,
                                            liftover=liftover)
            upload_pipeline = UploadPipeline.objects.create(uploaded_file=uploaded_file)
            process_upload_pipeline(upload_pipeline)


VCF_ROW = Tuple[str, int, int, str, str]


def _get_build_liftover_vcf_tuples(allele_source: AlleleSource, inserted_genome_build: GenomeBuild) -> Dict[Any, Dict[Any, List[VCF_ROW]]]:
    """ ID column set to allele_id """
    other_build_contigs_q_list = []
    other_builds = set()
    other_build_chrom_contig_id_mappings = {}
    for genome_build in GenomeBuild.builds_with_annotation():
        if genome_build != inserted_genome_build:
            other_builds.add(genome_build)
            other_build_chrom_contig_id_mappings[genome_build] = genome_build.get_chrom_contig_id_mappings()
            q = Q(variantallele__variant__locus__contig__in=genome_build.contigs)
            other_build_contigs_q_list.append(q)

    if not other_builds:
        return {}  # Nothing to do

    other_build_contigs_q = reduce(operator.or_, other_build_contigs_q_list)

    allele_qs = allele_source.get_allele_qs().select_related("clingen_allele")
    allele_contigs = defaultdict(set)
    # We want to do a left outer join to variant allele
    qs = Allele.objects.filter(other_build_contigs_q, pk__in=allele_qs)
    for allele_id, contig_id in qs.values_list("pk", "variantallele__variant__locus__contig"):
        allele_contigs[allele_id].add(contig_id)

    build_liftover_vcf_tuples = defaultdict(lambda: defaultdict(list))

    for allele in allele_qs:
        existing_contigs = allele_contigs[allele.pk]
        for genome_build in other_builds:
            chrom_to_contig = other_build_chrom_contig_id_mappings[genome_build]
            conversion_tool = None
            variant_tuple = None
            try:
                conversion_tool, variant_tuple = allele.get_liftover_variant_tuple(genome_build)
            except (Contig.ContigNotInBuildError, GenomeFasta.ContigNotInFastaError):
                log_traceback()

            if variant_tuple:
                # Converted ok - return VCF tuples in desired genome build
                chrom, position, ref, alt = variant_tuple
                contig_id = chrom_to_contig[chrom]
                if contig_id not in existing_contigs:
                    avt = (chrom, position, allele.pk, ref, alt)
                    build_liftover_vcf_tuples[genome_build][conversion_tool].append(avt)
            elif settings.LIFTOVER_NCBI_REMAP_ENABLED:
                if allele.liftovererror_set.filter(liftover__genome_build=genome_build,
                                                   liftover__conversion_tool=AlleleConversionTool.NCBI_REMAP).exists():
                    continue  # Skip as already failed NCBI liftover to desired build

                # Return VCF tuples in inserted genome build
                chrom, position, ref, alt = allele.variant_for_build(inserted_genome_build).as_tuple()
                if alt == Variant.REFERENCE_ALT:
                    alt = "."  # NCBI works with '.' but not repeating ref (ie ref = alt)
                avt = (chrom, position, allele.pk, ref, alt)
                build_liftover_vcf_tuples[genome_build][AlleleConversionTool.NCBI_REMAP].append(avt)

    return build_liftover_vcf_tuples
