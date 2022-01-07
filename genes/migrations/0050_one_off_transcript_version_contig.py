# Generated by Django 3.2.4 on 2021-12-12 23:00
from typing import Dict

from django.db import migrations


def _get_chrom_contig_mappings(contigs) -> Dict[str, 'Contig']:
    # Copied from GenomeBuild as we can't use models in migrations
    chrom_contig_mappings = {}
    for contig in contigs:
        chrom_contig_mappings[contig.name] = contig
        chrom_contig_mappings[contig.ucsc_name] = contig
        chrom_contig_mappings[contig.genbank_accession] = contig
        chrom_contig_mappings[contig.refseq_accession] = contig
    # Map lowercase "mt" -> "MT"
    chrom_contig_mappings["mt"] = chrom_contig_mappings["MT"]
    return chrom_contig_mappings


def _one_off_transcript_version_contig(apps, schema_editor):
    GenomeBuild = apps.get_model("snpdb", "GenomeBuild")
    Contig = apps.get_model("snpdb", "Contig")
    TranscriptVersion = apps.get_model("genes", "TranscriptVersion")

    bad_tvs = TranscriptVersion.objects.filter(data__chrom__isnull=True)
    if num_bad_tvs := bad_tvs.count():
        print(f"Deleting {num_bad_tvs} legacy TranscriptVersion records missing 'chrom' entries")
        _, deleted = bad_tvs.delete()
        deleted.pop("genes.TranscriptVersion", None)  # Expected
        if deleted:
            raise ValueError(f"Unexpected CASCADE deletion from removing bad TranscriptVersion records: {deleted=}")

    for genome_build in GenomeBuild.objects.all():
        contigs = Contig.objects.filter(genomebuildcontig__genome_build=genome_build)
        chrom_contig_mappings = _get_chrom_contig_mappings(contigs)
        transcript_versions = []
        for tv in TranscriptVersion.objects.filter(genome_build=genome_build):
            if chrom := tv.data.get("chrom"):
                tv.contig = chrom_contig_mappings[chrom]
                transcript_versions.append(tv)

        if num_update := len(transcript_versions):
            print(f"Setting contig on {num_update} {genome_build.name} transcript versions")
            TranscriptVersion.objects.bulk_update(transcript_versions, fields=["contig"], batch_size=2000)


class Migration(migrations.Migration):

    dependencies = [
        ('genes', '0049_transcriptversion_contig'),
    ]

    operations = [
        migrations.RunPython(_one_off_transcript_version_contig),
    ]
