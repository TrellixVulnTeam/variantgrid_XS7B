import operator
from functools import reduce
from typing import Optional, List

from django.db import models
from django.db.models.deletion import SET_NULL
from django.db.models.query_utils import Q

from analysis.models.enums import ZygosityNodeZygosity
from analysis.models.gene_counts import NodeGenesCountCollection
from analysis.models.nodes.analysis_node import AnalysisNode
from analysis.models.nodes.cohort_mixin import AncestorSampleMixin
from annotation.models.models import VariantAnnotation
from snpdb.models import Sample


class ZygosityNode(AncestorSampleMixin, AnalysisNode):
    sample = models.ForeignKey(Sample, null=True, on_delete=SET_NULL)
    zygosity = models.CharField(max_length=1, choices=ZygosityNodeZygosity.CHOICES, null=True)
    exclude = models.BooleanField(default=False)

    def _get_configuration_errors(self) -> List:
        errors = super()._get_configuration_errors()
        if not self.sample:
            errors.append("No sample selected.")
        return errors

    def modifies_parents(self):
        return self.sample and self.zygosity

    def get_zygosity_name(self):
        return dict(ZygosityNodeZygosity.CHOICES)[self.zygosity]

    def get_sample_q(self):
        if self.zygosity == ZygosityNodeZygosity.MULTIPLE_HIT:  # Let everything through
            sample_q = AnalysisNode.q_all()
        else:
            zygosity = self.zygosity
            field = self.sample.get_cohort_genotype_field("zygosity")
            sample_q = Q(**{f"{field}": zygosity})
        return sample_q

    def _get_node_q(self) -> Optional[Q]:
        sample_q = self.get_sample_q()
        q_list = [sample_q]
        if self.zygosity == ZygosityNodeZygosity.MULTIPLE_HIT:
            parent = self.get_single_parent()
            # Need to pass in kwargs in case we have parent (eg VennNode) that doesn't have needed annotation kwargs
            annotation_kwargs = self.get_annotation_kwargs(**kwargs)
            parent_qs = parent.get_queryset(extra_filters_q=sample_q, extra_annotation_kwargs=annotation_kwargs)
            gene_counts_qs = NodeGenesCountCollection.get_or_create_gene_counts_qs_for_node(self, parent_qs)
            genes_with_compound_het_qs = gene_counts_qs.filter(count__gte=2).values('gene_id')
            q_list.append(Q(**{VariantAnnotation.GENE_COLUMN + "__in": genes_with_compound_het_qs}))

        node_q: Q = reduce(operator.and_, q_list)
        if self.exclude:
            node_q = ~node_q
        return node_q

    def _get_method_summary(self):
        if self.modifies_parents():
            zygosity_name = self.get_zygosity_name()
            method_summary = f"Filtering to '{zygosity_name}'"
        else:
            method_summary = 'No filters applied as no zygosity selected.'

        return method_summary

    def get_node_name(self):
        name = ''
        if self.modifies_parents():
            name = self.get_zygosity_name()
        return name

    @staticmethod
    def get_help_text() -> str:
        return "Filter by sample zygosity"

    @staticmethod
    def get_node_class_label():
        return "Zygosity"
