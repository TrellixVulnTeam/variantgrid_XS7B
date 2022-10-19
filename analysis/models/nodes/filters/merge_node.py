import operator
import time
from collections import defaultdict
from functools import reduce
from typing import Optional, Counter

from django.db.models import Q

from analysis.models.nodes.analysis_node import AnalysisNode
from snpdb.models import lazy


class MergeNode(AnalysisNode):
    min_inputs = 1
    max_inputs = AnalysisNode.PARENT_CAP_NOT_SET

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache_node_q = False  # can't pickle querysets

    def modifies_parents(self):
        return self._num_unique_parents_in_queryset > 1

    @lazy
    def _num_unique_parents_in_queryset(self):
        parent_q_dicts = set()
        for p in self.get_non_empty_parents(require_parents_ready=False):
            key = tuple(((k, tuple(v)) for k, v in p.get_arg_q_dict().items()))
            parent_q_dicts.add(key)
        return len(parent_q_dicts)

    def get_single_parent(self):
        """ Override so we can use get_grid_node_id_and_version
            The query AND the input samples must be the same """

        if self._num_unique_parents_in_queryset == 1:
            my_sample_ids = self.get_sample_ids()
            for parent in self.get_non_empty_parents():  # As only 1 unique, can take 1st we find
                if parent.get_sample_ids() == my_sample_ids:
                    # print(f"MergeNode using {parent} as single unmodified parent!")
                    return parent
        return super().get_single_parent()  # Will throw exception due to multiple samples

    def _get_arg_q_dict_from_parents_and_node(self):
        # Go through and get the common things to all parents
        start = time.time()
        parent_arg_q_dict = {}
        arg_q_count = defaultdict(Counter)
        all_q_by_hash = {}
        for parent in self.get_non_empty_parents():
            arg_q_dict = parent.get_arg_q_dict(disable_cache=True)
            parent_arg_q_dict[parent] = arg_q_dict

            for k, q_dict in arg_q_dict.items():
                for q_hash, q in q_dict.items():
                    all_q_by_hash[q_hash] = q
                    arg_q_count[k][q_hash] += 1

        num_non_empty_parents = len(parent_arg_q_dict)
        # Find the ones that are common (in all)
        all_arg_q_dict = defaultdict(dict)
        for k, q_count in arg_q_count.items():
            print("-" * 20)
            print(f"{k=}")
            for q_hash, count in q_count.items():
                print(f"{q_hash}: {count=}")
                if count == num_non_empty_parents:
                    q = all_q_by_hash[q_hash]
                    all_arg_q_dict[k][q_hash] = q

        print("all_arg_q_dict:")
        print(all_arg_q_dict)

        # TODO: Go and knock them out of the others, and leave only what's unique
        arg_q_dict = {}
        q_or = []

        for parent in self.get_non_empty_parents():
            qs = parent.get_queryset(disable_cache=True)  # TODO: Pass in modified/unique arg_q_dict here
            q_or.append(Q(pk__in=qs.values_list("pk", flat=True)))

        arg_q_dict[None] = {self._get_node_q_hash(): reduce(operator.or_, q_or)}

        end = time.time()
        print(f"merge calculations took {end-start} secs")
        return arg_q_dict

    def _get_node_q(self) -> Optional[Q]:
        raise NotImplementedError("This should never be called")

    def _get_method_summary(self):
        parent_names = ','.join([p.name for p in self.get_parent_subclasses()])
        return f"Merged from parents: {parent_names}"

    def get_node_name(self):
        return "Merge"

    @staticmethod
    def get_help_text() -> str:
        return "Merge variants from multiple parents"

    @staticmethod
    def get_node_class_label():
        return "Merge"
