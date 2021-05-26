import logging

import pandas as pd
from dateutil import parser
from django.contrib.auth.models import User
from django.utils.timezone import make_aware

from analysis.models import VariantTagsImport, ImportedVariantTag, VariantTag, TagLocation
from library.vcf_utils import write_vcf_from_tuples
from snpdb.clingen_allele import populate_clingen_alleles_for_variants
from snpdb.liftover import create_liftover_pipelines
from snpdb.models import GenomeBuild, Variant, ImportSource, Tag, VariantAlleleCollectionSource, VariantAllele, \
    VariantAlleleCollectionRecord
from upload.models import UploadedVariantTags, UploadStep
from upload.tasks.vcf.import_vcf_step_task import ImportVCFStepTask
from variantgrid.celery import app


class VariantTagsCreateVCFTask(ImportVCFStepTask):
    """ Write a VCF with variants in VariantTags so they can go through normal insert pipeline """

    def process_items(self, upload_step):
        logging.info("VariantTagsCreateVCFTask - ready to go here!!!")
        upload_pipeline = upload_step.upload_pipeline
        uploaded_file = upload_pipeline.uploaded_file

        df = pd.read_csv(upload_step.input_filename)
        NEW_CLASSIFICATION = "New Classification"
        REMOVE_LENGTH = len(NEW_CLASSIFICATION)

        # view_genome_build should all be the same
        view_genome_builds = set(df["view_genome_build"])
        if len(view_genome_builds) != 1:
            raise ValueError(f"Expected 'view_genome_build' column to have 1 unique value, was: {view_genome_builds}")
        genome_build = GenomeBuild.get_name_or_alias(view_genome_builds.pop())
        # Create VariantTagsImport - everything hangs off this
        variant_tags_import = VariantTagsImport.objects.create(user=uploaded_file.user, genome_build=genome_build)
        UploadedVariantTags.objects.create(uploaded_file=uploaded_file, variant_tags_import=variant_tags_import)

        variant_tuples = []
        imported_tags = []
        for _, row in df.iterrows():
            variant_string = row["variant_string"]
            if variant_string.endswith(NEW_CLASSIFICATION):
                variant_string = variant_string[:-REMOVE_LENGTH].strip()

            variant_tuple = Variant.get_tuple_from_string(variant_string, genome_build=genome_build)
            variant_tuples.append(variant_tuple)
            node_id = None
            if "node__id" in row:
                node_id = row["node__id"]

            gene_symbol = row["variant__variantannotation__transcript_version__gene_version__gene_symbol__symbol"]
            created = parser.parse(row["created"])
            created = make_aware(created)
            ivt = ImportedVariantTag(variant_tags_import=variant_tags_import,
                                     variant_string=variant_string,
                                     genome_build_string=row["view_genome_build"],
                                     gene_symbol_string=gene_symbol,
                                     tag_string=row["tag__id"],
                                     variant_id=row["variant__id"],
                                     analysis_id=row["analysis__id"],
                                     node_id=node_id,
                                     analysis_name=row["analysis__name"],
                                     user_name=row["user__username"],
                                     created=created)
            imported_tags.append(ivt)

        items_processed = len(imported_tags)
        if imported_tags:
            ImportedVariantTag.objects.bulk_create(imported_tags, batch_size=2000)

        write_vcf_from_tuples(upload_step.output_filename, variant_tuples)
        return items_processed


class VariantTagsInsertTask(ImportVCFStepTask):
    """ This is run after the VCF import data insertion stage.
        Variants will be in database, and redis at this stage """

    def process_items(self, upload_step: UploadStep):
        uploaded_file = upload_step.upload_pipeline.uploaded_file
        uploaded_variant_tags = uploaded_file.uploadedvarianttags
        variant_tags_import = uploaded_variant_tags.variant_tags_import
        logging.info("_create_tags_from_variant_tags_import: %s!!", variant_tags_import)

        genome_build = variant_tags_import.genome_build

        tag_cache = {}
        user_cache = {}
        variant_tags = []
        created_date = []
        for ivt in variant_tags_import.importedvarianttag_set.all():
            tag = tag_cache.get(ivt.tag_string)
            if tag is None:
                tag, _ = Tag.objects.get_or_create(pk=ivt.tag_string)
                tag_cache[tag.pk] = tag

            variant_tuple = Variant.get_tuple_from_string(ivt.variant_string, genome_build=genome_build)
            variant = Variant.get_from_tuple(variant_tuple, genome_build)

            # We're not going to link anaysis/nodes - as probably don't match up across systems
            analysis = None
            node = None

            # Try and match user up to one on our system. If not there, use user from import
            user = user_cache.get(ivt.user_name)
            if user is None:
                try:
                    user = User.objects.get(username=ivt.user_name)
                except User.DoesNotExist:
                    user = variant_tags_import.user
                user_cache[ivt.user_name] = user

            # TODO: We should also look at not creating dupes somehow??
            vt = VariantTag(variant=variant,
                            genome_build=genome_build,
                            tag=tag,
                            analysis=analysis,
                            location=TagLocation.EXTERNAL,
                            imported_variant_tag=ivt,
                            node=node,
                            user=user)

            created_date.append(ivt.created)
            variant_tags.append(vt)

        variant_list = []
        if variant_tags:
            logging.info("Creating %d variant tags", len(variant_tags))
            # VariantTag.created will be set by auto_now_add (no way to stop this)
            variant_tags = VariantTag.objects.bulk_create(variant_tags, batch_size=2000)
            # Update date to be from imported date
            for vt, created in zip(variant_tags, created_date):
                vt.created = created
                variant_list.append(vt.variant)
            VariantTag.objects.bulk_update(variant_tags, fields=["created"], batch_size=2000)

        logging.info("Creating liftover pipelines")
        populate_clingen_alleles_for_variants(genome_build, variant_list)
        allele_source = VariantAlleleCollectionSource.objects.create(genome_build=genome_build)
        va_collection_records = []
        for va in VariantAllele.objects.filter(variant__in=variant_list):
            va_collection_records.append(VariantAlleleCollectionRecord(collection=allele_source, variant_allele=va))
        VariantAlleleCollectionRecord.objects.bulk_create(va_collection_records, batch_size=2000)
        create_liftover_pipelines(variant_tags_import.user, allele_source, ImportSource.WEB, genome_build)


VariantTagsCreateVCFTask = app.register_task(VariantTagsCreateVCFTask())
VariantTagsInsertTask = app.register_task(VariantTagsInsertTask())