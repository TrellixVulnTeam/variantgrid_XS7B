from collections import defaultdict

from django.core.management import BaseCommand

from classification.classification_import import reattempt_variant_matching
from classification.models import Classification
from genes.models import TranscriptVersion, TranscriptVersionSequenceInfo
from genes.models_enums import AnnotationConsortium
from library.guardian_utils import admin_bot


class Command(BaseCommand):

    def handle(self, *args, **options):

        # Get a list of transcripts/genome build used by classifications
        build_transcript_classification_ids = defaultdict(lambda: defaultdict(list))
        for c in Classification.objects.all():
            if transcript := c.transcript:
                build_transcript_classification_ids[c.get_genome_build()][transcript].append(c.pk)

        # We have to deal with bumping transcripts etc, so probably the best way to go is find the ones that would be
        # OK and then anything else is assumed to need re-matching
        # This will also get LRGs
        classification_ids_to_rematch = []
        for genome_build, transcript_classification_ids in build_transcript_classification_ids.items():
            # Things that have gaps, NR etc will not be returned so will forced to rematch
            previously_good_tv_qs = TranscriptVersion.objects.filter(genome_build=genome_build,
                                                                     data__chrom__isnull=False,
                                                                     data__cdna_match__isnull=True,
                                                                     data__partial__isnull=True,
                                                                     transcript__identifier__startswith='NM_')
            previously_good_transcripts_by_accessions = {}
            for tv in previously_good_tv_qs:
                previously_good_transcripts_by_accessions[tv.accession] = tv

            # For RefSeq - do batch API calls as they're much faster
            KNOWN_BAD_LIST = {"NM_0000529.2"}
            refseq_transcripts = []
            for transcript_accession in transcript_classification_ids.keys():
                if transcript_accession.startswith("LRG"):
                    continue
                if "." not in transcript_accession:  # Transcript w/o version
                    continue
                if transcript_accession in KNOWN_BAD_LIST:
                    continue

                try:
                    TranscriptVersion.get_transcript_id_and_version(transcript_accession)
                except ValueError:
                    print(f"Skipping badly formed transcript accession: '{transcript_accession}'")
                    continue

                try:
                    if AnnotationConsortium.get_from_transcript_accession(transcript_accession) == AnnotationConsortium.REFSEQ:
                        refseq_transcripts.append(transcript_accession)
                except ValueError as ve:
                    print(f"Skipping {transcript_accession}: {ve}")
                    continue

            print("Batch retrieving RefSeq TranscriptVersionSequenceInfo...")
            # Some of these are bad, so will cause the batch to fail.
            TranscriptVersionSequenceInfo.get_refseq_transcript_versions(refseq_transcripts,
                                                                         entrez_batch_size=100,
                                                                         fail_on_error=False)
            # Try to get at least some of the failed data via batches
            TranscriptVersionSequenceInfo.get_refseq_transcript_versions(refseq_transcripts,
                                                                         entrez_batch_size=20,
                                                                         fail_on_error=False)
            print("Finished retrieving batch info")

            for t, classifications in transcript_classification_ids.items():
                if transcript := previously_good_transcripts_by_accessions.get(t):
                    # Will used cached data from API if available from above
                    if not transcript.alignment_gap:
                        continue
                classification_ids_to_rematch.extend(classifications)

        classification_qs = Classification.objects.filter(pk__in=classification_ids_to_rematch)
        num_classifications = classification_qs.count()
        print(f"Rematching {num_classifications} classifications")

        # Revalidate
        user = admin_bot()
        print(f"Revalidating...")
        for c in classification_qs:
            c.revalidate(user)

        print(f"Rematching...")
        valid_record_count, invalid_record_count = reattempt_variant_matching(user, classification_qs)
        print(f"{valid_record_count=}, {invalid_record_count=}")
