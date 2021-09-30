import gzip
import json
import logging
from typing import Dict, List, Set

from django.core.management.base import BaseCommand
from genes.models import GeneSymbol, GeneAnnotationImport, Gene, GeneVersion, TranscriptVersion, Transcript
from genes.models_enums import AnnotationConsortium
from library.file_utils import open_handle_gzip
from snpdb.models.models_genome import GenomeBuild


class Command(BaseCommand):
    BATCH_SIZE = 2000

    def add_arguments(self, parser):
        consortia = [ac[1] for ac in AnnotationConsortium.choices]
        builds = [gb.name for gb in GenomeBuild.builds_with_annotation()]

        parser.add_argument('--dry-run', action='store_true', help="Don't actually modify anything")
        parser.add_argument('--genome-build', choices=builds, required=True)
        parser.add_argument('--annotation-consortium', choices=consortia, required=True)
        parser.add_argument('--release', required=False,
                            help="Make a release (to match VEP) store all gene/transcript versions")
        parser.add_argument('--save-merged-file', help="Write a file (requires pyreference-json)")
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--pyreference-json', nargs="+", action="extend", help='PyReference JSON.gz')
        group.add_argument('--merged-json', help='Merged JSON (from multiple PyReference files)')

    def handle(self, *args, **options):
        if pyreference_json := options["pyreference_json"]:
            pyreference_data = []
            for prj_filename in pyreference_json:
                logging.info("Loading %s", prj_filename)
                with open_handle_gzip(prj_filename) as f:
                    pyreference_data.append(json.load(f))
            merged_data = self._convert_to_merged_data(pyreference_data)
            if save_merged_file := options["save_merged_file"]:
                logging.info("Writing '%s'", save_merged_file)
                with gzip.open(save_merged_file, 'w') as outfile:
                    json_str = json.dumps(merged_data)
                    outfile.write(json_str.encode('ascii'))
                    exit(0)
        elif merged_json := options["merged_json"]:
            with open_handle_gzip(merged_json) as f:
                merged_data = json.load(f)
        else:
            raise ValueError("You need to specify at least one of '--pyreference-json' or '--merged-json'")

        self._import_merged_data(merged_data)

    @staticmethod
    def _get_most_recent_transcripts(pyreference_data) -> List[Set]:
        transcripts_in_files = [set(prd["transcripts_by_id"]) for prd in pyreference_data]
        most_recent_transcripts = []
        all_transcripts = set()
        for tif in reversed(transcripts_in_files):
            unique_transcripts = tif - all_transcripts
            most_recent_transcripts.append(unique_transcripts)
            all_transcripts |= unique_transcripts
        most_recent_transcripts.reverse()
        return most_recent_transcripts

    def _convert_to_merged_data(self, pyreference_data: List[Dict]) -> List[Dict]:
        """ We want to make the minimal amount of data to insert - so only keep the last copy of transcripts """
        print("_convert_to_merged_data")
        most_recent_transcripts = self._get_most_recent_transcripts(pyreference_data)

        merged_data = []
        for prd, transcripts in zip(pyreference_data, most_recent_transcripts):
            gene_version = {}
            transcript_versions = {}
            transcript_gene_version = {}

            for gene_id, gene in prd["genes_by_id"].items():
                version = gene.get("version", 0)
                gv_accession = f"{gene_id}.{version}"
                need_gene = False
                for transcript_accession in gene["transcripts"]:
                    if transcript_accession in transcripts:
                        transcript_gene_version[transcript_accession] = gv_accession

                if need_gene:
                    gene_version[gene_id] = convert_gene_pyreference_to_gene_version_data(gene)

            for transcript_accession in transcripts:
                transcript = prd["transcripts_by_id"][transcript_accession]
                tv_data = {
                    "biotype": transcript["biotype"],
                    "gene_version": transcript_gene_version[transcript_accession],
                    "data": convert_transcript_pyreference_to_pyhgvs(transcript),
                }
                transcript_versions[transcript_accession] = tv_data

            if transcript_versions:
                data = {
                    "gene_annotation_import": prd["reference_gtf"],
                    "gene_version": gene_version,
                    "transcript_versions": transcript_versions,
                }
                merged_data.append(data)

        return merged_data

    def _import_merged_data(self, genome_build: GenomeBuild, annotation_consortium, merged_data: List[Dict]):
        """        """
        print("_import_merged_data")

        known_gene_symbols = set(GeneSymbol.objects.all().values_list("pk", flat=True))
        genes_qs = Gene.objects.filter(annotation_consortium=annotation_consortium)
        known_genes_ids = {genes_qs.values_list("identifier", flat=True)}
        transcripts_qs = Transcript.objects.filter(annotation_consortium=annotation_consortium)
        known_transcript_ids = {transcripts_qs.values_list("identifier", flat=True)}

        gene_version_qs = GeneVersion.objects.filter(genome_build=genome_build,
                                                     annotation_consortium=annotation_consortium)
        known_gene_version_ids_by_accession = {f"{gene_id}.{version}": pk for (pk, gene_id, version) in gene_version_qs.values_list("pk", "gene_id", "version")}
        transcript_version_qs = TranscriptVersion.objects.filter(genome_build=genome_build,
                                                                 annotation_consortium=annotation_consortium)
        known_transcript_version_ids_by_accession = {f"{transcript_id}.{version}": pk for (pk, transcript_id, version) in transcript_version_qs.values_list("pk", "transcript_id", "version")}

        for data in merged_data:
            import_data = data["gene_annotation_import"]
            logging.info("%s has %d transcripts", import_data, len(data["transcript_versions"]))
            import_source = GeneAnnotationImport.objects.create(annotation_consortium=annotation_consortium,
                                                                genome_build=genome_build,
                                                                filename=import_data["path"],
                                                                url=import_data["url"],
                                                                file_md5sum=import_data["md5sum"])

            new_gene_symbols = []
            new_genes = []
            new_gene_versions = []
            modified_gene_versions = []

            for gene_id, gv_data in data["gene_version"].items():
                if gene_id not in known_genes_ids:
                    new_genes.append(Gene(identifier=gene_id,
                                          annotation_consortium=annotation_consortium))

                if symbol := gv_data["gene_symbol"]:
                    if symbol not in known_gene_symbols:
                        new_gene_symbols.append(GeneSymbol(symbol=symbol))
                # RefSeq have no version, set as 0 if missing
                version = gv_data.get("version", 0)

                gene_version = GeneVersion(gene_id=gene_id,
                                           version=version,
                                           gene_symbol_id=symbol,
                                           hgnc_id=gv_data.get("hgnc"),
                                           description=gv_data.get("description"),
                                           biotype=gv_data.get("biotype"),
                                           genome_build=genome_build,
                                           import_source=import_source)
                gv_accession = f"{gene_id}.{version}"
                if pk := known_gene_version_ids_by_accession.get(gv_accession):
                    gene_version.pk = pk
                    modified_gene_versions.append(gene_version)
                else:
                    new_gene_versions.append(gene_version)

            if new_gene_symbols:
                logging.info("Creating %d new gene symbols", len(new_gene_symbols))
                GeneSymbol.objects.bulk_create(new_gene_symbols, batch_size=self.BATCH_SIZE)

            if new_genes:
                logging.info("Creating %d new genes", len(new_genes))
                Gene.objects.bulk_create(new_genes, batch_size=self.BATCH_SIZE)

            if new_gene_versions:
                logging.info("Creating %d new gene versions", len(new_gene_versions))
                GeneVersion.objects.bulk_create(new_gene_versions, batch_size=self.BATCH_SIZE)

            # Update with newly inserted gene versions - so that we have a PK to use below
            known_gene_version_ids_by_accession.update({f"{gv.gene_id}.{gv.version}" for gv in new_gene_versions})

            # Could potentially be duplicate gene versions (diff transcript versions from diff GFFs w/same GeneVersion)
            if modified_gene_versions:
                logging.info("Updating %d gene versions", len(modified_gene_versions))
                GeneVersion.objects.bulk_update(modified_gene_versions,
                                                ["gene_symbol_id", "hgnc_id", "description", "biotype", "import_source"],
                                                batch_size=self.BATCH_SIZE)

            new_transcripts = []
            new_transcript_versions = []
            modified_transcript_versions = []

            for transcript_accession, tv_data in data["transcript_version"].items():
                transcript_id, version = TranscriptVersion.get_transcript_id_and_version(transcript_accession)
                if transcript_id not in known_transcript_ids:
                    new_transcripts.append(Transcript(identifier=transcript_id,
                                                      annotation_consortium=annotation_consortium))

                gene_version_id = known_gene_version_ids_by_accession[tv_data["gene_version"]]
                transcript_version = TranscriptVersion(transcript_id=transcript_id,
                                                       version=version,
                                                       gene_version_id=gene_version_id,
                                                       genome_build=genome_build,
                                                       import_source=import_source,
                                                       biotype=tv_data["biotype"],
                                                       data=tv_data["data"])
                if pk := known_transcript_version_ids_by_accession.get(transcript_accession):
                    transcript_version.pk = pk
                    modified_transcript_versions.append(transcript_version)
                else:
                    new_transcript_versions.append(transcript_version)

            if new_transcripts:
                logging.info("Creating %d new transcripts", len(new_transcripts))
                Transcript.objects.bulk_create(new_transcripts, batch_size=self.BATCH_SIZE)

            if new_transcript_versions:
                logging.info("Creating %d new transcript versions", len(new_transcript_versions))
                TranscriptVersion.objects.bulk_create(new_transcript_versions, batch_size=self.BATCH_SIZE)

            if modified_transcript_versions:
                logging.info("Updating %d transcript versions", len(modified_transcript_versions))
                TranscriptVersion.objects.bulk_update(modified_transcript_versions,
                                                      ["gene_version_id", "import_source", "biotype", "data"],
                                                      batch_size=self.BATCH_SIZE)


def convert_gene_pyreference_to_gene_version_data(gene_data: Dict) -> Dict:
    gene_version_data = {
        'biotype': ",".join(gene_data["biotype"]),
        'description': gene_data.get("description"),
        'gene_symbol': gene_data["name"],
    }

    if hgnc_str := gene_data.get("HGNC"):
        # Has HGNC: (5 characters) at start of it
        gene_version_data["hgnc"] = hgnc_str[5:]

    # Only Ensembl Genes have versions
    if version := gene_data.get("version"):
        gene_data["version"] = version

    return gene_version_data


def convert_transcript_pyreference_to_pyhgvs(transcript_data: Dict) -> Dict:
    start = transcript_data["start"]
    end = transcript_data["stop"]
    strand = transcript_data["strand"]
    # PyHGVS has cds_start/cds_end be equal to start/end for non-coding transcripts
    cds_start = transcript_data.get("cds_start", start)
    cds_end = transcript_data.get("cds_end", end)
    # PyHGVS exons are in genomic order, PyReference are in stranded
    features = transcript_data["features_by_type"]
    exons = [[ed["start"], ed["stop"]] for ed in features["exon"]]
    cdna_match = [cdm.get("gap") for cdm in features.get("cDNA_match", [])]

    if strand == '-':
        exons.reverse()
        cdna_match.reverse()

    pyhgvs_data = {
        'chrom': transcript_data["chr"],
        'start': start,
        'end': end,
        'strand': strand,
        'cds_start': cds_start,
        'cds_end': cds_end,
        'exons': exons,
    }

    # Optional stuff
    if cdna_match:
        pyhgvs_data["cdna_match"] = cdna_match
    if transcript_data.get("partial"):
        pyhgvs_data["partial"] = 1

    return pyhgvs_data

