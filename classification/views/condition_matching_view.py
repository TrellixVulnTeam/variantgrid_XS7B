from typing import Dict, Any

from django.db.models import QuerySet
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from guardian.shortcuts import get_objects_for_user

from classification.models import ConditionTextMatch, ConditionText, update_condition_text_match_counts
from library.utils import empty_to_none
from ontology.ontology_matching import normalize_condition_text
from snpdb.views.datatable_view import DatatableConfig, RichColumn, SortOrder
import re


class ConditionTextColumns(DatatableConfig):

    def __init__(self, request):
        super().__init__(request)

        self.rich_columns = [
            RichColumn(key="lab__name", label='Lab', orderable=True, sort_keys=['lab__name', 'normalized_text']),
            RichColumn(key="normalized_text", label='Text', orderable=True, client_renderer="idRenderer", extra_columns=["id"], sort_keys=['normalized_text', 'lab__name']),
            RichColumn(key="classifications_count", label="Classifications Affected", orderable=True, sort_keys=['classifications_count', 'normalized_text']),
            RichColumn(key="classifications_count_outstanding", label="Classifications Outstanding", orderable=True, sort_keys=['classifications_count_outstanding', 'normalized_text'])
        ]

    def get_initial_queryset(self):
        # exclude where we've auto matched and have 0 outstanding left
        return get_objects_for_user(self.user, ConditionText.get_read_perm(), klass=ConditionText, accept_global_perms=True)

    def filter_queryset(self, qs: QuerySet) -> QuerySet:
        if filter_text := empty_to_none(self.get_query_param("text_filter")):
            normal_text = normalize_condition_text(filter_text)
            words = [word.strip() for word in normal_text.split(" ")]
            for word in words:
                qs = qs.filter(normalized_text__icontains=word)
        return qs


def condition_matchings_view(request):
    return render(request, 'classification/condition_matchings.html', context={
        'datatable_config': ConditionTextColumns(request)
    })


def condition_matching_view(request, pk: int):
    ct: ConditionText = get_object_or_404(ConditionText.objects.filter(pk=pk))

    if request.method == 'POST':
        ct.check_can_write(request.user)
        condition_match_pattern = re.compile("condition-match-([0-9]+)")
        key: str
        for key, value in request.POST.items():
            if match := condition_match_pattern.match(key):
                match_id = int(match[1])
                # do secondary check to make sure we're only editing one ConditionText at at time
                ctm: ConditionTextMatch
                if ctm := ConditionTextMatch.objects.filter(condition_text=ct, pk=match_id).first():
                    ctm.update_with_condition_matching_str(value)
                    ctm.save()
                else:
                    print(f"Couldn't find ConditionMatchText record {match_id}")

        ct.last_edited_by = request.user
        update_condition_text_match_counts(ct)
        ct.save()

        return redirect(reverse('condition_matching', kwargs={"pk": pk}))

    ct.check_can_view(request.user)

    root_match = get_object_or_404(ConditionTextMatch.objects.filter(condition_text=ct, gene_symbol__isnull=True))

    return render(request, 'classification/condition_matching.html', context={
        'condition_text': ct,
        'condition_match': root_match
    })
