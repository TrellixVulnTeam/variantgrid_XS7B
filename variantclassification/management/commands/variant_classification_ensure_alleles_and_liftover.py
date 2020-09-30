from django.conf import settings
from django.core.management.base import BaseCommand

from library.guardian_utils import admin_bot
from library.utils import get_git_hash
from snpdb.clingen_allele import populate_clingen_alleles_for_variants
from snpdb.liftover import create_liftover_pipelines
from snpdb.models.models_genome import GenomeBuild
from snpdb.models.models_enums import ImportSource
from variantclassification.autopopulate_evidence_keys.evidence_from_variant import get_clingen_allele_and_evidence_value_for_variant
from variantclassification.enums import SpecialEKeys, SubmissionSource
from variantclassification.models.variant_classification import VariantClassification, AllClassificationsAlleleSource


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--add-clingen-allele', action='store_true',
                            help="Add 'clingen_allele_id' to VariantClassifications missing it")

    def handle(self, *args, **options):
        script = __file__
        add_clingen_allele = options["add_clingen_allele"]
        for genome_build in GenomeBuild.builds_with_annotation():
            defaults = {"git_hash": get_git_hash(settings.BASE_DIR)}
            allele_source, _ = AllClassificationsAlleleSource.objects.get_or_create(script=script,
                                                                                    genome_build=genome_build,
                                                                                    defaults=defaults)
            variants_qs = allele_source.get_variants_qs()
            if variants_qs.count():
                print(f"{genome_build} has variants - creating Allele/ClinGen + liftover")
                populate_clingen_alleles_for_variants(genome_build, variants_qs)
                create_liftover_pipelines(admin_bot(), allele_source, ImportSource.COMMAND_LINE, genome_build)

                if add_clingen_allele:
                    # Patch those ClinGen alleles into the variant classifications
                    num_added_clingen_allele = 0
                    clingen_allele_key_null = "evidence__%s__isnull" % SpecialEKeys.CLINGEN_ALLELE_ID
                    for vc in VariantClassification.objects.filter(variant__in=variants_qs,
                                                                   **{clingen_allele_key_null: True}):
                        _, evidence_value, _ = get_clingen_allele_and_evidence_value_for_variant(genome_build,
                                                                                                 vc.variant)
                        vc.patch_value({SpecialEKeys.CLINGEN_ALLELE_ID: evidence_value},
                                       source=SubmissionSource.VARIANT_GRID)
                        vc.save()
                        num_added_clingen_allele += 1

                    print(f"Added {SpecialEKeys.CLINGEN_ALLELE_ID} to {num_added_clingen_allele} classifications")
