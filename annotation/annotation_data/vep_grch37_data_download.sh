#!/bin/bash

# This downloads the files we can get straight from the web

DISK_FREE_CWD=$(df -Ph . | tail -1 | awk '{print $4}')

echo "This will take a lot of space - make sure you're have a lot of disk space!"
echo "You are in $(pwd), on a drive with ${DISK_FREE_CWD} free."

echo "Fasta"
mkdir -p fasta
cd fasta
# Need to bgzip see https://asia.ensembl.org/info/docs/tools/vep/script/vep_cache.html#fasta
wget --quiet -O - https://ftp.ncbi.nlm.nih.gov/genomes/refseq/vertebrate_mammalian/Homo_sapiens/all_assembly_versions/GCF_000001405.25_GRCh37.p13/GCF_000001405.25_GRCh37.p13_genomic.fna.gz | gzip -d | bgzip >  GCF_000001405.25_GRCh37.p13_genomic.fna.gz
samtools faidx GCF_000001405.25_GRCh37.p13_genomic.fna.gz
cd ..

mkdir -p annotation_data/all_builds/maxentscan
if [[ ! -e annotation_data/all_builds/maxentscan ]]; then
  cd annotation_data/all_builds
  wget http://hollywood.mit.edu/burgelab/maxent/download/fordownload.tar.gz
  tar xvfz ~/Downloads/fordownload.tar.gz
  mv fordownload maxentscan
  cd ../..
fi

mkdir -p annotation_data/GRCh37
cd annotation_data/GRCh37

echo "Conservation"
wget ftp://hgdownload.soe.ucsc.edu/goldenPath/hg19/phastCons100way/hg19.100way.phastCons.bw
wget --recursive --no-parent -R "index.html*" ftp://hgdownload.soe.ucsc.edu/goldenPath/hg19/phastCons46way/placentalMammals/

wget ftp://hgdownload.soe.ucsc.edu/goldenPath/hg19/phyloP100way/hg19.100way.phyloP100way.bw
wget --recursive --no-parent -R "index.html*" ftp://hgdownload.soe.ucsc.edu/goldenPath/hg19/phyloP46way/placentalMammals/

echo "Population databases"
wget ftp://ftp.ensembl.org/pub/data_files/homo_sapiens/GRCh37/variation_genotype/TOPMED_GRCh37.vcf.gz
wget ftp://ftp.ensembl.org/pub/data_files/homo_sapiens/GRCh37/variation_genotype/TOPMED_GRCh37.vcf.gz.tbi

wget ftp://ftp.ensembl.org/pub/data_files/homo_sapiens/GRCh37/variation_genotype/UK10K_COHORT.20160215.sites.vcf.gz
wget ftp://ftp.ensembl.org/pub/data_files/homo_sapiens/GRCh37/variation_genotype/UK10K_COHORT.20160215.sites.vcf.gz.tbi

# repeatmasker_hg19.bed.gz


cd ../..