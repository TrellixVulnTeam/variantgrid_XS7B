from datetime import datetime
from typing import Optional

from django.contrib import messages
from django.db.models.functions import Length
from django.http import StreamingHttpResponse
from django.shortcuts import render
from classification.models import ConditionText, top_level_suggestion, condition_matching_suggestions
from genes.models import GeneSymbol
from library.log_utils import report_exc_info
from library.utils import delimited_row
from ontology.ontology_matching import OntologyMatching, SearchText, normalize_condition_text


def condition_match_test_download_view(request):

    def result_iterator():
        try:
            row_count = 0
            yield delimited_row([
                "id", "lab", "text", "gene", "terms", "messages"
            ])

            ct: ConditionText
            for ct in ConditionText.objects.annotate(text_len=Length('normalized_text'))\
                              .filter(text_len__gte=3)\
                              .select_related('lab')\
                              .order_by('-classifications_count'):
                if ct.normalized_text == "not provided":
                    continue

                suggestions = condition_matching_suggestions(ct, ignore_existing=True)
                for suggestion in suggestions:
                    status = None
                    gene_symbol = suggestion.condition_text_match.gene_symbol
                    if suggestion.condition_text_match.is_root:
                        if suggestion.is_auto_assignable():
                            status = "auto-assign"
                    elif suggestion.condition_text_match.is_gene_level:
                        # got a gene level suggestion, but since we got it via condition_matching_suggstions
                        # is auto-assignable isn't trustworthy as it may not match the root terms
                        # TODO update condition_matching_suggestions so is_auto_assignable is accurate
                        if suggestion.is_auto_assignable(gene_symbol):
                            if auto_suggstion := top_level_suggestion(ct.normalized_text):
                                if auto_suggstion.is_auto_assignable(gene_symbol):
                                    suggestion = auto_suggstion
                                    status = "auto-assign"
                    if not suggestion.terms:
                        if suggestion.messages:
                            status = "notes"
                        else:
                            status = "manual only"
                    elif status is None:
                        status = "suggestion"

                    yield delimited_row([
                        ct.id,
                        ct.lab.name,
                        ct.normalized_text,
                        gene_symbol.symbol if gene_symbol else None,
                        "\n".join([term.id + " " + term.name for term in suggestion.terms]),
                        "\n".join([message.severity + " " + message.text for message in suggestion.messages]),
                        status
                    ])

                row_count += 1

        except GeneratorExit:
            pass
        except Exception:
            report_exc_info()
            raise

    response = StreamingHttpResponse(result_iterator(), content_type='text/csv')
    modified_str = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")  # e.g. 'Wed, 21 Oct 2015 07:28:00 GMT'

    response['Last-Modified'] = modified_str
    response['Content-Disposition'] = f'attachment; filename="text_automatching_{modified_str}.csv"'
    return response


def condition_match_test_view(request):
    condition_text = request.GET.get("condition_text")
    gene_symbol_str = request.GET.get("gene_symbol")
    auto_matches = list()
    attempted = False
    suggestion = None
    gene_symbol: Optional[GeneSymbol] = None

    valid = False
    if condition_text:
        valid = True
        if gene_symbol_str:
            gene_symbol = GeneSymbol.objects.filter(symbol=gene_symbol_str).first()
            if not gene_symbol:
                messages.add_message(request, messages.WARNING, f"Could not find Gene Symbol '{gene_symbol_str}'")
                valid = False
    if valid:
        auto_matches = OntologyMatching.from_search(condition_text, gene_symbol_str)
        suggestion = top_level_suggestion(normalize_condition_text(condition_text))
        attempted = True

    context = {
        "condition_text": condition_text,
        "search_text": SearchText(condition_text) if condition_text else None,
        "gene_symbol": gene_symbol_str,
        "auto_matches": auto_matches,
        "suggestion": suggestion,
        "is_auto_assignable": suggestion.is_auto_assignable(gene_symbol) if suggestion else None,
        "attempted": attempted
    }

    return render(request, 'classification/condition_match_test.html', context=context)