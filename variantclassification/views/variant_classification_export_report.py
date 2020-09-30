from typing import Optional

from django.http import StreamingHttpResponse, HttpResponse
from django.template import engines
import re

from annotation.citations import get_citations
from snpdb.models import Organization
from variantclassification.enums.variant_classification_enums import SpecialEKeys
from variantclassification.models.evidence_key import EvidenceKeyMap
from variantclassification.models.variant_classification import VariantClassificationModification, \
    VariantClassification
from variantclassification.models import VariantClassificationJsonParams
from variantclassification.views.variant_classification_export_utils import ExportFormatter


class ExportFormatterReport(ExportFormatter):
    """
    Formats using report for the corresponding lab.
    Typically you'd only use for a single record
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def row_iterator(self):
        return self.qs.all()

    def header(self) -> Optional[str]:
        return None

    def export(self, as_attachment: bool = True):
        self.prepare_groups()

        row_datas = list()
        org: Optional[Organization] = None
        for vcm in self.raw_qs:
            row_data = self.row_data(vcm)
            row_datas.append(row_data)
            org = vcm.variant_classification.lab.organization
            # only support 1 record for now
            break

        template_str = org.classification_report_template or f'No report template has been configured for {org.name}'
        django_engine = engines['django']
        template = django_engine.from_string(template_str)
        content = template.render({'record': row_datas[0]})

        response = HttpResponse(content=content, content_type=self.content_type())
        if as_attachment:
            response['Content-Disposition'] = f'attachment; filename="{self.filename()}"'
        return response

    def row_data(self, record: VariantClassificationModification) -> dict:
        context = {}
        evidence = record.as_json(VariantClassificationJsonParams(self.user, include_data=True))['data']
        e_keys = EvidenceKeyMap(lab=record.variant_classification.lab)

        for e_key in e_keys.all_keys:
            blob = evidence.get(e_key.key) or {}

            report_blob = dict()
            report_blob['value'] = blob.get('value', None)
            report_blob['note'] = blob.get('note', None)
            report_blob['formatted'] = e_key.pretty_value(blob)
            report_blob['label'] = e_key.pretty_label
            context[e_key.key] = report_blob

        context['citations'] = [dict(citation._asdict()) for citation in get_citations(record.citations)]
        context['evidence_weights'] = VariantClassification.summarize_evidence_weights(evidence)
        context['acmg_criteria'] = record.criteria_strength_summary(e_keys)
        return context

    def content_type(self) -> str:
        return 'text/html'

    def filename(self) -> str:
        return self.generate_filename(prefix='report', include_genome_build=False, extension='html')
