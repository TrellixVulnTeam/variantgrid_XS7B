import itertools
import json
import re
import pandas as pd
import pronto
from django.core.management import BaseCommand
from django.db import transaction

from annotation.models import HPOSynonymScope
from library.file_utils import file_md5sum
from ontology.models import OntologyService, OntologyRelation
from ontology.ontology_builder import OntologyBuilder, OntologyBuilderDataUpToDateException


"""
MONDO import file can be found http://www.obofoundry.org/ontology/mondo.html
Importing it will provide MONDO and OMIM terms
"""

ID_EXTRACT_P = re.compile(r"^.*\/([A-Z]+)_([0-9]+)$")
HGNC_EXTRACT_P = re.compile(r"http://identifiers.org/hgnc/([0-9]+)")
OMIM_URL_P = re.compile(r"http://identifiers.org/omim/([0-9]+)")
GENE_SYMBOL_SEARCH = re.compile(r"([A-Z][A-Z,0-9]{2,})")
OMIM_P = re.compile("OMIM:[0-9]+")

GENE_RELATIONS = {
    "http://purl.obolibrary.org/obo/RO_0004025": "disease causes dysfunction of",
    "http://purl.obolibrary.org/obo/RO_0004001": "has material basis in gain of function germline mutation in",
    "http://purl.obolibrary.org/obo/RO_0004021": "disease has basis in disruption of",
    "http://purl.obolibrary.org/obo/RO_0004020": "disease has basis in dysfunction of"
}

MATCH_TYPES = {
    "http://www.w3.org/2004/02/skos/core#exactMatch": OntologyRelation.EXACT,
    "http://www.w3.org/2004/02/skos/core#closeMatch": OntologyRelation.CLOSE,
    "http://www.w3.org/2004/02/skos/core#broadMatch": OntologyRelation.BROAD,
    "http://www.w3.org/2004/02/skos/core#narrowMatch": OntologyRelation.NARROW
}

"""
TODO - this runs pretty slow (due to many redundant update_or_create) calls.
Rework it so we can keep a cache of everything already updated or created this run

"""

@transaction.atomic
def load_mondo(filename: str, force: bool):
    data_file = None
    with open(filename, 'r') as json_file:
        data_file = json.load(json_file)

    file_hash = file_md5sum(filename)

    ontology_builder = OntologyBuilder(
        filename=filename,
        context="mondo_file",
        ontology_service=OntologyService.MONDO,
        force_update=force)

    ontology_builder.ensure_hash_changed(data_hash=file_hash)  # don't re-import if hash hasn't changed

    print("This may take a few minutes")
    node_to_hgnc_id: [str, str] = dict()
    node_to_mondo: [str, str] = dict()
    count = 0

    for graph in data_file.get("graphs", []):
        print("Reviewing Nodes")
        for node in graph.get("nodes", []):
            if node.get("type") == "CLASS":

                if node_id_full := node.get("id"):
                    if match := ID_EXTRACT_P.match(node_id_full):
                        type = match[1]
                        index = match[2]
                        full_id = f"{type}:{index}"
                        if type != "MONDO":
                            continue

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

                            if synonyms := meta.get("synonyms"):
                                for synonym in synonyms:
                                    pred = synonym.get("pred")
                                    if pred == "hasExactSynonym":
                                        # val = synonym.get("val")
                                        for xref in synonym.get("xrefs", []):
                                            if OMIM_P.match(xref):
                                                ontology_builder.add_term(
                                                    term_id=xref,
                                                    name=label,
                                                    definition=f"Name copied from synonym {full_id}",
                                                    primary_source=False
                                                )
                                                ontology_builder.add_ontology_relation(
                                                    source_term_id=full_id,
                                                    dest_term_id=xref,
                                                    relation=OntologyRelation.EXACT,
                                                )

                            # for synonym in meta.get("synonyms", []):
                            #    synonym_value = synonym.get("val")
                            # if synonym_value:
                            #    synonyms.append(synonym_value)
                            #    genes_mentioned = genes_mentioned.union(set(GENE_SYMBOL_SEARCH.findall(synonym_value)))
                            node_to_mondo[node_id_full] = full_id

                            for bp in meta.get("basicPropertyValues", []):
                                val = bp.get("val")
                                if omim_match := OMIM_URL_P.match(val):
                                    omim = f"OMIM:{omim_match[1]}"
                                    pred = bp.get("pred")
                                    pred = MATCH_TYPES.get(pred, pred)

                                    ontology_builder.add_term(
                                        term_id=omim,
                                        name=label,
                                        definition=f"Name copied from synonym {full_id}",
                                        primary_source=False
                                    )
                                    ontology_builder.add_ontology_relation(
                                        source_term_id=full_id,
                                        dest_term_id=omim,
                                        relation=pred
                                    )

                    # copy of id for gene symbol to gene symbol
                    elif match := HGNC_EXTRACT_P.match(node_id_full):
                        gene_symbol = node.get("lbl")
                        hgnc_id = match[1]
                        term_id = f"HGNC:{hgnc_id}"
                        ontology_builder.add_term(
                            term_id=f"HGNC:{hgnc_id}",
                            name=gene_symbol,
                            definition=None,
                            primary_source=False
                        )
                        node_to_hgnc_id[node_id_full] = term_id

        print("Reviewing edges")
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


@transaction.atomic
def load_hpo(filename: str, force: bool):
    ontology_builder = OntologyBuilder(
        filename=filename,
        context="hpo_file",
        ontology_service=OntologyService.HPO,
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
        synonyms = []
        for synonym in term.synonyms:
            scope = scope_lookup[synonym.scope]
            synonyms.append({
                "name": synonym.description,
                "scope": scope
            })
        if synonyms:
            extra = {"synonyms": synonyms}

        if not term_id.startswith(OntologyService.HPO):
            continue

        ontology_builder.add_term(
            term_id=term_id,
            name=term.name,
            extra=extra,
            definition=term.definition,
            primary_source=True
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


# @transaction.atomic
# def load_hpo_disease(filename: str, force: bool):
#     ontology_builder = OntologyBuilder(
#         filename=filename,
#         context="hpo_disease",
#         ontology_service=OntologyService.HPO,
#         force_update=force)
#     file_hash = file_md5sum(filename)
#     ontology_builder.ensure_hash_changed(data_hash=file_hash)  # don't re-import if hash hasn't changed
#     df = pd.read_csv(filename, index_col=None, comment='#', sep='\t',
#                      names=['disease_id', 'gene_symbol', 'gene_id', 'hpo_id', 'hpo_name'],
#                      dtype={"gene_id": int})
#     # TODO is gene_symbol, gene_id meant to come into play here?
#     gb = df.groupby(["hpo_id"])
#     for hpo_id, data in gb:
#         name = list(data["hpo_name"])[0]
#         ontology_builder.add_term(term_id=hpo_id, name=name, definition=None, extra=None, primary_source=False)
#         for disease_id in set(data["disease_id"]):
#             ontology_builder.add_ontology_relation(
#                 source_term_id=hpo_id,
#                 dest_term_id=disease_id,
#                 relation=OntologyRelation.FREQUENCY  # TODO do we have more information than this?
#             )
#     gb = df.groupby(["gene_id"])
#     for gene_id, data in gb:
#         name = list(data["gene_symbol"])[0]
#         hgnc_id = f"HGNC:{gene_id}"
#         ontology_builder.add_term(
#             term_id=f"HGNC:{gene_id}",
#             name=name,
#             definition=None,
#             primary_source=False
#         )
#         for omim_id in set(data["disease_id"]):
#             # TODO extra to provide more details about the association
#             ontology_builder.add_ontology_relation(
#                 source_term_id=omim_id,
#                 dest_term_id=hgnc_id,
#                 relation=OntologyRelation.FREQUENCY
#             )
#     ontology_builder.complete()
#     ontology_builder.report()


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--force', action="store_true")
        parser.add_argument('--mondo_json', required=False)
        parser.add_argument('--hpo_owl', required=False)
        # parser.add_argument('--hpo_to_omim', required=False)

    @transaction.atomic
    def handle(self, *args, **options):
        force = options.get("force")
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
        # if filename := options.get("hpo_to_omim"):
        #    try:
        #        load_hpo_disease(filename, force)
        #    except OntologyBuilderDataUpToDateException:
        #        print("HPO Disease hash is the same as last import")
