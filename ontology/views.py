from typing import List

from django.contrib import messages
from django.views.generic import TemplateView

from library.utils import LimitedCollection
from ontology.models import OntologyTerm, OntologyTermRelation, OntologyService, OntologySnake, OntologyRelation


class OntologyTermView(TemplateView):

    template_name = "ontology/ontology_term.html"

    def get_context_data(self, **kwargs):
        term_id = self.kwargs.get("term")
        term = OntologyTerm.get_or_stub(term_id)
        if not term.is_stub:
            gene_relationships = None
            if term.ontology_service != OntologyService.HGNC:
                gene_relationships = LimitedCollection(OntologySnake.snake_from(term=term, to_ontology=OntologyService.HGNC), 250)

            all_relationships: List[OntologyTermRelation] = OntologyTermRelation.relations_of(term)
            regular_relationships = list()
            parent_relationships = list()
            child_relationships = list()
            for relationship in all_relationships:
                if relationship.relation == OntologyRelation.IS_A:
                    if relationship.source_term == term:
                        parent_relationships.append(relationship)
                    else:
                        child_relationships.append(relationship)
                else:
                    regular_relationships.append(relationship)

            return {
                "term": term,
                "gene_relationships": gene_relationships,
                "parent_relationships": LimitedCollection(parent_relationships, 250),
                "regular_relationships": LimitedCollection(regular_relationships, 250),
                "child_relationships": LimitedCollection(child_relationships, 250)
            }
        messages.add_message(self.request, messages.ERROR, "This term is not stored in our database")
        return {"term": term}
