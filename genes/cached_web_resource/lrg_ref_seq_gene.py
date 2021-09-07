import ftplib
import logging
from io import BytesIO

import pandas as pd

from annotation.models import CachedWebResource
from genes.models import LRGRefSeqGene
from genes.models_enums import LRGRefSeqGeneCategory
from library.pandas_utils import df_nan_to_none


def store_lrg_ref_seq_gene_from_web(cached_web_resource: CachedWebResource):
    logging.info("Downloading 'LRG_RefSeqGene' via FTP")
    ftp = ftplib.FTP("ftp.ncbi.nlm.nih.gov")
    ftp.login("anonymous", "anonymous")
    buffer = BytesIO()
    ftp.retrbinary('RETR /refseq/H_sapiens/RefSeqGene/LRG_RefSeqGene', buffer.write)
    buffer.seek(0)

    df = pd.read_csv(buffer, sep='\t', error_bad_lines=False)
    lrg_mask = ~pd.isna(df["LRG"])
    lrg_df = df_nan_to_none(df[lrg_mask])

    lookup = {l.label: l.value for l in LRGRefSeqGeneCategory}
    lrg_records = []
    for _, row in lrg_df.iterrows():
        lrg_records.append(LRGRefSeqGene(cached_web_resource=cached_web_resource,
                                         lrg=row["LRG"],
                                         rna=row["RNA"],
                                         t=row["t"],
                                         category=lookup[row['Category']]))

    if num_records := len(lrg_records):
        LRGRefSeqGene.objects.bulk_create(lrg_records, ignore_conflicts=True, batch_size=2000)

    description = f"{num_records} LRG RefSeqGene mappings"
    logging.info("Inserted %s", description)

    cached_web_resource.description = description
    cached_web_resource.save()
