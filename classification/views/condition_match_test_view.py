from datetime import datetime
from django.contrib import messages
from django.db.models.functions import Length
from django.http import StreamingHttpResponse
from django.shortcuts import render

from classification.models import ConditionTextMatch, ConditionText, ConditionTextStatus
from genes.models import GeneSymbol
from library.log_utils import report_exc_info
from library.utils import delimited_row
from ontology.ontology_matching import OntologyMatching, SearchText


def condition_match_test_download_view(request):
    max_count = 10
    try:
        if row_count_str := request.POST.get("row_count"):
            max_count = int(row_count_str)
    except ValueError:
        pass

    def result_iterator():
        try:
            row_count = 0
            yield delimited_row([
                "id", "classification_count", "lab", "text", "gene_symbol", "tied_top_matches", "top_matches (max 5)", "score"
            ])

            ct: ConditionText
            for ct in ConditionText.objects.annotate(text_len=Length('normalized_text'))\
                              .filter(text_len__gte=3)\
                              .select_related('lab')\
                              .order_by('-classifications_count')[0:max_count]:
                ctm: ConditionTextMatch
                for ctm in ct.gene_levels:
                    from_search = OntologyMatching.from_search(search_text=ct.normalized_text, gene_symbol=ctm.gene_symbol.symbol)
                    top = from_search.top_terms()
                    classification_count = ConditionTextMatch.objects.filter(
                        condition_text=ctm.condition_text,
                        gene_symbol=ctm.gene_symbol,
                        classification__isnull=False
                    ).count()
                    if len(top) > 0:
                        yield delimited_row([
                            ct.id,
                            classification_count,
                            ct.lab.name,
                            ct.normalized_text,
                            ctm.gene_symbol.name,
                            len(top),
                            '\n'.join([match.term.id + " " + match.term.name for match in top[0:5]]),
                            int(top[0].score)
                        ])
                        row_count += 1

                if row_count >= max_count:
                    return

        except GeneratorExit:
            pass
        except Exception:
            report_exc_info()

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

    valid = True
    if condition_text:
        if gene_symbol_str:
            gene_symbol = GeneSymbol.objects.filter(symbol=gene_symbol_str).first()
            if not gene_symbol:
                messages.add_message(request, messages.WARNING, f"Could not find Gene Symbol '{gene_symbol_str}'")
                valid = False
    if valid:
        auto_matches = OntologyMatching.from_search(condition_text, gene_symbol_str)
        attempted = True

    context = {
        "condition_text": condition_text,
        "search_text": SearchText(condition_text) if condition_text else None,
        "gene_symbol": gene_symbol_str,
        "auto_matches": auto_matches,
        "attempted": attempted
    }

    return render(request, 'classification/condition_match_test.html', context=context)