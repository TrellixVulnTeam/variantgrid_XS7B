import ftplib
import gzip
import logging
from collections import defaultdict
from io import BytesIO, TextIOWrapper
from typing import Dict

from Bio import SwissProt

from annotation.models import CachedWebResource
from genes.models import UniProt

FUNCTION_KEY = "FUNCTION: "
TISSUE_SPEC_KEY = "TISSUE SPECIFICITY: "
PATHWAY_KEY = "PATHWAY: "
PID_KEY = "Pathway_Interaction_DB"
REACTOME_KEY = "Reactome"


def store_uniprot_from_web(cached_web_resource: CachedWebResource):
    logging.info("Downloading 'uniprot_sprot_human.dat.gz' via FTP")
    ftp = ftplib.FTP("ftp.uniprot.org")
    ftp.login("anonymous", "anonymous")
    buffer = BytesIO()
    ftp.retrbinary('RETR /pub/databases/uniprot/current_release/knowledgebase/taxonomic_divisions/uniprot_sprot_human.dat.gz', buffer.write)
    buffer.seek(0)

    with gzip.GzipFile(fileobj=buffer) as f:
        text_f = TextIOWrapper(f)
        logging.info("Extracting data")
        uniprot_data = extract_uniprot_sprot(text_f)

    logging.info("Creating DB records")
    uniprot_records = []
    for accession, data in uniprot_data.items():
        if data:
            uniprot_records.append(UniProt(accession=accession, cached_web_resource=cached_web_resource, **data))
        else:
            print(f"{accession} had no data we care about!")

    UniProt.objects.bulk_create(uniprot_records, batch_size=2000)

    cached_web_resource.description = f"{len(uniprot_records)} UniProt records"
    cached_web_resource.save()


def extract_uniprot_sprot(f) -> Dict:
    """ Based on Jinghua (Frank) Feng's code - construct gene reference data  """
    reader = SwissProt.parse(f)

    uniprot = defaultdict(lambda: defaultdict(set))
    for record in reader:
        # only use Primary (citable) accession number
        accession = record.accessions[0]
        if accession in uniprot:
            print(f"Adding to existing accession: {accession}")

        for c in record.comments:
            if c.startswith(FUNCTION_KEY):
                uniprot[accession]["function"].add(c.replace(FUNCTION_KEY, '', 1))  # Delete Function_key
            elif c.startswith(TISSUE_SPEC_KEY):
                uniprot[accession]["tissue_specificity"].add(c.replace(TISSUE_SPEC_KEY, '', 1))
            elif c.startswith(PATHWAY_KEY):
                uniprot[accession]["pathway"].add(c.replace(PATHWAY_KEY, '', 1))

        for xfre in record.cross_references:
            if xfre[0] == PID_KEY:
                # ('Pathway_Interaction_DB', 'aurora_a_pathway', 'Aurora A signaling')
                uniprot[accession]["pathway_interaction_db"].add(xfre[2])
            elif xfre[0] == REACTOME_KEY:
                # ('Reactome', 'REACT_111183', 'Meiosis')
                uniprot[accession]["reactome"].add(xfre[2])

    return uniprot
