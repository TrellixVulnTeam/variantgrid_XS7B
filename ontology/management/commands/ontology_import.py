import itertools
import json
import re
import csv
from dataclasses import dataclass
from typing import List, Optional

import pandas as pd
import pronto
from django.core.management import BaseCommand

from annotation.models.models_enums import HPOSynonymScope
from genes.models import HGNC
from library.file_utils import file_md5sum
from ontology.models import OntologyService, OntologyRelation, OntologyTerm, OntologyImportSource, OntologyImport
from ontology.ontology_builder import OntologyBuilder, OntologyBuilderDataUpToDateException
from model_utils.models import now

"""
MONDO import file can be found http://www.obofoundry.org/ontology/mondo.html
Importing it will provide MONDO and OMIM terms
"""

GENE_SYMBOL_SEARCH = re.compile(r"([A-Z][A-Z,0-9]{2,})")

GENE_RELATIONS = {
    "http://purl.obolibrary.org/obo/RO_0004025": "disease causes dysfunction of",
    "http://purl.obolibrary.org/obo/RO_0004001": "has material basis in gain of function germline mutation in",
    "http://purl.obolibrary.org/obo/RO_0004021": "disease has basis in disruption of",
    "http://purl.obolibrary.org/obo/RO_0004020": "disease has basis in dysfunction of",
    "http://purl.obolibrary.org/obo/RO_0004026": "disease has location",
    "http://purl.obolibrary.org/obo/RO_0004027": "disease has inflammation site",
    "http://purl.obolibrary.org/obo/RO_0004030": "disease arises from structure"
}

MATCH_TYPES = {
    "http://www.w3.org/2004/02/skos/core#exactMatch": OntologyRelation.EXACT,
    "http://www.w3.org/2004/02/skos/core#closeMatch": OntologyRelation.CLOSE,
    "http://www.w3.org/2004/02/skos/core#broadMatch": OntologyRelation.BROAD,
    "http://www.w3.org/2004/02/skos/core#narrowMatch": OntologyRelation.NARROW,
    "http://www.geneontology.org/formats/oboInOwl#hasAlternativeId": OntologyRelation.ALTERNATIVE,
    "http://purl.obolibrary.org/obo/IAO_0100001": OntologyRelation.REPLACED
}

"""
TODO - this runs pretty slow (due to many redundant update_or_create) calls.
Rework it so we can keep a cache of everything already updated or created this run
"""

ID_OBO = re.compile("^http://purl[.]obolibrary[.]org/obo/([A-Z]+)_([0-9]+)$")
ID_IDENTIFIERS = re.compile("http://identifiers[.]org/([A-Za-z]+)/([0-9]+)$")
ID_STRAIGHT = re.compile("^([A-Z]+):([0-9]+)$")


@dataclass
class TermId:
    type: str = None
    index: str = None

    def __init__(self, qualified_ref: str):
        for pattern in [ID_OBO, ID_IDENTIFIERS, ID_STRAIGHT]:
            if match := pattern.match(qualified_ref):
                self.type = match[1].upper()
                self.index = match[2]
                return

    @property
    def id(self) -> str:
        return f"{self.type}:{self.index}"


def load_mondo(filename: str, force: bool):
    data_file = None

    file_hash = file_md5sum(filename)

    ontology_builder = OntologyBuilder(
        filename=filename,
        context="mondo_file",
        import_source=OntologyService.MONDO,
        force_update=force,
        processor_version=3)

    ontology_builder.ensure_hash_changed(data_hash=file_hash)  # don't re-import if hash hasn't changed

    with open(filename, 'r') as json_file:
        data_file = json.load(json_file)

    print("This may take a few minutes")
    node_to_hgnc_id: [str, str] = dict()
    node_to_mondo: [str, str] = dict()

    for graph in data_file.get("graphs", []):

        print("** Reviewing Nodes")
        for node in graph.get("nodes", []):

            if node_id_full := node.get("id"):
                term = TermId(node_id_full)
                if term.type == "MONDO":
                    full_id = term.id
                    node_to_mondo[node_id_full] = full_id

                    if meta := node.get("meta"):
                        label = node.get("lbl")
                        extra = dict()

                        defn = meta.get("definition", {}).get("val")
                        if defn:
                            defn = defn.replace(".nn", ".\n")

                        # if defn:
                        #    genes_mentioned = genes_mentioned.union(
                        #        set(GENE_SYMBOL_SEARCH.findall(defn)))
                        if synonyms := meta.get("synonyms"):
                            extra["synonyms"] = synonyms

                        # make the term early so we don't have to create stubs for it if we find relationships
                        ontology_builder.add_term(
                            term_id=full_id,
                            name=label,
                            definition=defn,
                            extra=extra if extra else None,
                            primary_source=True
                        )

                        synonym_set = set()
                        if synonyms := meta.get("synonyms"):

                            # only allow 1 relationship between any 2 terms (though DB does allow more)
                            # storing all of them would be more "accurate" but gets in the way of our usage
                            # prioritise relationships as EXACT, RELATED, related terms, XREF
                            for synonym in synonyms:
                                pred = synonym.get("pred")
                                if pred == "hasExactSynonym":
                                    # val = synonym.get("val")
                                    for xref in synonym.get("xrefs", []):
                                        xref_term = TermId(xref)
                                        if xref_term.type in {"HP", "OMIM"}:
                                            ontology_builder.add_term(
                                                term_id=xref,
                                                name=label,
                                                definition=f"Name copied from synonym {full_id}",
                                                primary_source=False
                                            )
                                            ontology_builder.add_ontology_relation(
                                                source_term_id=full_id,
                                                dest_term_id=xref,
                                                relation=OntologyRelation.EXACT
                                            )
                                            synonym_set.add(xref)

                            # look at related synonyms second, if we have RELATED, don't bother with any other relationships
                            for synonym in synonyms:
                                pred = synonym.get("pred")
                                if pred == "hasRelatedSynonym":
                                    # val = synonym.get("val")
                                    for xref in synonym.get("xrefs", []):
                                        xref_term = TermId(xref)
                                        if xref_term.type in {"HP", "OMIM"} and not xref_term.id in synonym_set:
                                            ontology_builder.add_term(
                                                term_id=xref_term.id,
                                                name=label,
                                                definition=f"Name copied from related synonym {full_id}",
                                                primary_source=False
                                            )
                                            ontology_builder.add_ontology_relation(
                                                source_term_id=full_id,
                                                dest_term_id=xref_term.id,
                                                relation=OntologyRelation.RELATED
                                            )
                                            synonym_set.add(xref_term.id)
                        #end synonymns

                        for bp in meta.get("basicPropertyValues", []):
                            val = TermId(bp.get("val"))
                            if val.type in {"HP", "OMIM"} and not val.id in synonym_set:
                                pred = bp.get("pred")
                                pred = MATCH_TYPES.get(pred, pred)

                                ontology_builder.add_term(
                                    term_id=val.id,
                                    name=label,
                                    definition=f"Name copied from {pred} synonym {full_id}",
                                    primary_source=False
                                )
                                ontology_builder.add_ontology_relation(
                                    source_term_id=full_id,
                                    dest_term_id=val.id,
                                    relation=pred
                                )
                            synonym_set.add(val.id)

                        if xrefs := meta.get("xrefs"):
                            for xref in xrefs:
                                val = TermId(xref.get("val"))
                                if val.type in {"HP", "OMIM"} and val.id not in synonym_set:
                                    ontology_builder.add_term(
                                        term_id=val.id,
                                        name=label,
                                        definition=f"Name copied from xref synonym {full_id}",
                                        primary_source=False
                                    )
                                    ontology_builder.add_ontology_relation(
                                        source_term_id=full_id,
                                        dest_term_id=val.id,
                                        relation=OntologyRelation.XREF
                                    )

                # copy of id for gene symbol to gene symbol
                elif term.type == "HGNC":
                    gene_symbol = node.get("lbl")
                    ontology_builder.add_term(
                        term_id=term.id,
                        name=gene_symbol,
                        definition=None,
                        primary_source=False
                    )
                    node_to_hgnc_id[node_id_full] = term.id

        print("** Reviewing axioms")
        if axioms := graph.get("logicalDefinitionAxioms"):
            for axiom in axioms:
                defined_class_id = TermId(axiom.get("definedClassId"))
                if defined_class_id.type != "MONDO":
                    continue

                genus_ids = [TermId(genus) for genus in axiom.get("genusIds")]
                mondo_genus = [term for term in genus_ids if term.type == "MONDO"]

                for restriction in axiom.get("restrictions"):

                    filler = TermId(restriction.get("fillerId"))
                    if filler.type != "HGNC":
                        continue

                    relation = GENE_RELATIONS.get(restriction.get("propertyId"))
                    if relation is None:
                        print("Unexpected relationship " + restriction.get("propertyId"))
                        continue

                    ontology_builder.add_ontology_relation(
                        source_term_id=defined_class_id.id,
                        dest_term_id=filler.id,
                        extra={"via": ", ".join([m.id for m in mondo_genus])},
                        relation=relation
                    )
                    for term in mondo_genus:
                        ontology_builder.add_ontology_relation(
                            source_term_id=term.id,
                            dest_term_id=filler.id,
                            relation=relation
                        )

        print("** Reviewing edges")

        for edge in graph.get("edges", []):

            subject_id: str = edge.get("sub")
            obj_id: str = edge.get("obj")
            relationship = edge.get("pred")

            if mondo_subject_id := node_to_mondo.get(subject_id):
                if hgnc_id := node_to_hgnc_id.get(obj_id):
                    relationship = GENE_RELATIONS.get(relationship, relationship)
                    ontology_builder.add_ontology_relation(
                        source_term_id=mondo_subject_id,
                        dest_term_id=hgnc_id,
                        relation=relationship
                    )

                # TODO support other relationships
                elif mondo_obj_id := node_to_mondo.get(obj_id):
                    if relationship == "is_a":
                        ontology_builder.add_ontology_relation(
                            source_term_id=mondo_subject_id,
                            dest_term_id=mondo_obj_id,
                            relation=OntologyRelation.IS_A
                        )
    print("Purging old data")
    ontology_builder.complete()
    ontology_builder.report()
    print("Committing...")


def load_hpo(filename: str, force: bool):
    ontology_builder = OntologyBuilder(
        filename=filename,
        context="hpo_file",
        import_source=OntologyImportSource.HPO,
        processor_version=2,
        force_update=force)

    file_hash = file_md5sum(filename)
    ontology_builder.ensure_hash_changed(data_hash=file_hash)  # don't re-import if hash hasn't changed
    print("About to pronto the file")
    ot = pronto.Ontology(filename)
    print("Pronto complete")
    scope_lookup = {v.upper(): k for k, v in HPOSynonymScope.choices}

    for term in ot.terms():
        term_id = str(term.id)

        extra = None
        detailed_aliases = []
        aliases = set()
        for synonym in term.synonyms:
            aliases.add(synonym.description)
            scope = scope_lookup[synonym.scope]
            detailed_aliases.append({
                "name": synonym.description,
                "scope": scope
            })
        if detailed_aliases:
            extra = {"synonyms": detailed_aliases}

        if not term_id.startswith(OntologyService.HPO):
            continue

        ontology_builder.add_term(
            term_id=term_id,
            name=term.name,
            extra=extra,
            definition=term.definition,
            primary_source=True,
            aliases=list(aliases)
        )

        children = itertools.islice(term.subclasses(), 1, None)
        for kid_term in children:

            if not kid_term.id.startswith(OntologyService.HPO):
                continue

            ontology_builder.add_ontology_relation(
                dest_term_id=term.id,
                source_term_id=kid_term.id,
                relation=OntologyRelation.IS_A
            )
    ontology_builder.complete()
    ontology_builder.report()
    print("Committing...")


def load_hpo_disease(filename: str, force: bool):
    ontology_builder = OntologyBuilder(
        filename=filename,
        context="hpo_disease",
        import_source=OntologyImportSource.HPO,
        processor_version=5,
        force_update=force)
    file_hash = file_md5sum(filename)
    ontology_builder.ensure_hash_changed(data_hash=file_hash)  # don't re-import if hash hasn't changed
    df = pd.read_csv(filename, index_col=None, comment='#', sep='\t',
                     names=['disease_id', 'gene_symbol', 'gene_id', 'hpo_id', 'hpo_name'],
                     dtype={"gene_id": int})

    by_hpo = df.groupby(["hpo_id"])
    for hpo_id, by_hpo_data in by_hpo:
        # make HPO stubs in case HPO import hasn't happened yet
        hpo_name = by_hpo_data["hpo_name"].iloc[0]
        ontology_builder.add_term(
            term_id=hpo_id,
            name=hpo_name,
            definition=None,
            primary_source=False
        )

        by_omim = by_hpo_data.groupby(["disease_id"])
        for omim_id, by_omim_data in by_omim:
            # link HPO -> OMIM
            ontology_builder.add_ontology_relation(
                source_term_id=hpo_id,
                dest_term_id=omim_id,
                relation=OntologyRelation.ALL_FREQUENCY
            )

    by_gene = df.groupby(["gene_symbol"])
    for gene_symbol, gene_data in by_gene:
        # IMPORTANT, the gene_id is the entrez gene_id, not the HGNC gene id
        try:
            hgnc_term = OntologyTerm.get_gene_symbol(gene_symbol)

            by_omim = gene_data.groupby(["disease_id"])
            for omim_id, by_omim_data in by_omim:
                ontology_builder.add_ontology_relation(
                    source_term_id=omim_id,
                    dest_term_id=hgnc_term.id,
                    relation=OntologyRelation.ENTREZ_ASSOCIATION
                )
        except ValueError:
            print(f"Could not resolve gene symbol {gene_symbol} to HGNC ID")

    ontology_builder.complete()
    ontology_builder.report()


def load_biomart(filename: str, force: bool):
    MIM_DESCRIPTION = "MIM morbid description"
    MIM_ACCESSION = "MIM morbid accession"

    ontology_builder = OntologyBuilder(
        filename=filename,
        context="biomart_omim_aliases",
        import_source="biomart",
        processor_version=3,
        force_update=force)
    file_hash = file_md5sum(filename)
    ontology_builder.ensure_hash_changed(data_hash=file_hash)

    # Create MIMMorbid from BioMart file
    mim_biomart_df = pd.read_csv(filename, sep='\t').dropna().astype({"MIM morbid accession": int})
    for expected_col in [MIM_DESCRIPTION, MIM_ACCESSION]:
        if expected_col not in mim_biomart_df.columns:
            msg = f"file {filename} missing column: '{expected_col}': columns: '{mim_biomart_df.columns}'"
            raise ValueError(msg)

    mim_biomart_df = mim_biomart_df.set_index(MIM_ACCESSION)
    description_series = mim_biomart_df[MIM_DESCRIPTION]

    for mim_accession_id, description in description_series.items():
        descriptions_list = [x for x in str(description).split(";;")]
        name = descriptions_list[0]
        aliases = [name] + [term for term in [term.strip() for term in str(description).split(";")] if term]
        ontology_builder.add_term(
            term_id=f"OMIM:{mim_accession_id}",
            name=name,
            definition=None,
            primary_source=False, # primary source is now the OMIM file if it's available
            aliases=aliases
        )

    ontology_builder.complete()
    ontology_builder.report()


def load_omim(filename: str, force: bool):
    ontology_builder = OntologyBuilder(
        filename=filename,
        context="omim_file",
        import_source=OntologyImportSource.OMIM,
        processor_version=2,
        force_update=force)

    file_hash = file_md5sum(filename)
    ontology_builder.ensure_hash_changed(data_hash=file_hash)  # don't re-import if hash hasn't changed

    with open(filename, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t')
        next(csv_reader) # title row
        next(csv_reader) # date row (worth reading e.g. "Generated: 20201-02-04")
        header = next(csv_reader)
        OMIM_EXPECTED_HEADER = ["# Prefix", "MIM Number", "Preferred Title; symbol",	"Alternative Title(s); symbol(s)",	"Included Title(s); symbols"]
        MOVED_TO = re.compile("MOVED TO ([0-9]+)")
        if header != OMIM_EXPECTED_HEADER:
            raise ValueError(f"Header not as expected, got {header}")

        RELEVANT_PREFIXES = {
            # "Asterisk": "Gene",
            # "Plus": "Gene and phenotype, combined",
            "Number Sign": "Phenotype, molecular basis known",
            "Percent": "Phenotype or locus, molecular basis unknown",
            "NULL": "Other, mainly phenotypes with suspected mendelian basis",
            # "Caret": "Entry has been removed from the database or moved to another entry"
        }

        #["Number Sign", "Percent", "NULL"]

        for row in csv_reader:
            prefix = row[0]
            omim_type = RELEVANT_PREFIXES.get(prefix)
            if len(row) <= 1 or not omim_type:
                continue
            mim_number = row[1]
            preferred_title = row[2]
            alternative_terms = row[3]
            included_titles = row[4]

            moved_to: Optional[int] = None
            aliases = []

            if match := MOVED_TO.match(preferred_title):
                # This will only happen if you uncomment Caret
                moved_to = match.group(1)
                preferred_title = f"obsolete, see OMIM:{moved_to}"
            else:
                aliases.append(preferred_title)
                aliases += [term for term in [term.strip() for term in (preferred_title + " " + alternative_terms).split(";")] if term]

            extras = {"type": omim_type}
            if included_titles:
                extras["included_titles"] = included_titles

            ontology_builder.add_term(
                term_id=f"OMIM:{mim_number}",
                name=preferred_title,
                definition=None,
                aliases=aliases,
                extra=extras,
                primary_source=True
            )
            if moved_to:
                ontology_builder.add_ontology_relation(
                    source_term_id=f"OMIM:{mim_number}",
                    dest_term_id=f"OMIM:{moved_to}",
                    relation=OntologyRelation.REPLACED
                )
    ontology_builder.complete(purge_old_terms=True)
    ontology_builder.report()


def sync_hgnc():
    uploads: List[OntologyTerm] = list()

    o_import = OntologyImport.objects.create(
        import_source="HGNC Sync",
        filename="HGNC Aliases",
        context="hgnc_sync",
        hash="N/A",
        processor_version=1,
        processed_date=now,
        completed=True)

    for hgnc in HGNC.objects.all():
        uploads.append(OntologyTerm(
            id=f"HGNC:{hgnc.id}",
            ontology_service=OntologyService.HGNC,
            name=hgnc.gene_symbol_id,
            index=hgnc.id,
            definition=hgnc.approved_name,
            from_import=o_import
        ))

    old_count = OntologyTerm.objects.filter(ontology_service=OntologyService.HGNC).count()
    OntologyTerm.objects.bulk_create(uploads, ignore_conflicts=True)
    updated_count = OntologyTerm.objects.filter(ontology_service=OntologyService.HGNC).count()
    delta = updated_count - old_count
    print(f"Inserted {delta} records from HGNCGeneNames into OntologyTerm")


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--force', action="store_true")
        parser.add_argument('--mondo_json', required=False)
        parser.add_argument('--hpo_owl', required=False)
        parser.add_argument('--omim_frequencies', required=False)
        parser.add_argument('--hgnc_sync', action="store_true", required=False)
        parser.add_argument('--biomart', required=False)
        parser.add_argument('--omim', required=False)

    def handle(self, *args, **options):
        force = options.get("force")

        if options.get("hgnc_sync"):
            print("Syncing HGNC")
            sync_hgnc()

        if filename := options.get("omim"):
            try:
                load_omim(filename, force=force)
            except OntologyBuilderDataUpToDateException:
                print("OMIM File hash is the same as last import")

        if filename := options.get("biomart"):
            try:
                load_biomart(filename, force=force)
            except OntologyBuilderDataUpToDateException:
                print("BioMart File hash is the same as last import")

        if filename := options.get("mondo_json"):
            try:
                load_mondo(filename, force)
            except OntologyBuilderDataUpToDateException:
                print("MONDO File hash is the same as last import")

        if filename := options.get("hpo_owl"):
            try:
                load_hpo(filename, force)
            except OntologyBuilderDataUpToDateException:
                print("HPO File hash is the same as last import")

        if filename := options.get("omim_frequencies"):
            try:
                load_hpo_disease(filename, force)
            except OntologyBuilderDataUpToDateException:
                print("HPO Disease hash is the same as last import")
