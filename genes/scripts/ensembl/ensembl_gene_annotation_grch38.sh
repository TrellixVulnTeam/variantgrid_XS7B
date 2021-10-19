#!/bin/bash

# Skip earlier GTFs as they don't have versions
#for release in 76 77 78 79 80; do
#  filename=Homo_sapiens.GRCh38.${release}.gtf.gz
#  url=ftp://ftp.ensembl.org/pub/release-${release}/gtf/homo_sapiens/${filename}
#  if [[ ! -e ${filename} ]]; then
#    wget ${url}
#  fi

#  if [[ ! -e ${filename}.json.gz ]]; then
#    pyreference_gff_to_json.py --url "${url}" --gff3 "${filename}"
#  fi
#done

#81 is first GFF3 for GRCh38
pyreference_args=()
for release in 81 82 83 84 85 86 87 88 89 90 91 92 93 94 95 96 97 98 99 100 101 102 103 104; do
  filename=Homo_sapiens.GRCh38.${release}.gff3.gz
  url=ftp://ftp.ensembl.org/pub/release-${release}/gff3/homo_sapiens/${filename}
  pyreference_file=${filename}.json.gz

  if [[ ! -e ${filename} ]]; then
    wget ${url}
  fi
  if [[ ! -e ${filename}.json.gz ]]; then
    pyreference_gff_to_json.py --url "${url}" --gff3 "${filename}"
  fi
  pyreference_args+=(--pyreference-json ${pyreference_file})
done

VG_DIR=$(dirname $(dirname $(dirname $(dirname ${BASH_SOURCE[0]}))))
merged_file="vg_gene_annotation.ensembl.grch38.json.gz"
if [[ ! -e ${merged_file} ]]; then
  python3.8 ${VG_DIR}/manage.py import_gene_annotation2 --annotation-consortium=Ensembl --genome-build=GRCh38 \
    --save-merged-file=${merged_file} ${pyreference_args[@]}
fi