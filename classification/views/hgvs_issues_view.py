from dataclasses import dataclass
from typing import Dict, Any, Optional
from django.contrib.auth.decorators import user_passes_test
from django.db.models import QuerySet
from django.http import StreamingHttpResponse
from django.http.request import HttpRequest
from django.shortcuts import render
from lazy import lazy
from requests.models import Response

from classification.enums import SpecialEKeys
from classification.models import Classification, classification_flag_types
from flags.models import Flag, FlagStatus, FlagComment, FlagType
from flags.models.models import FlagCollection
from library.django_utils import get_url_from_view_path
from library.guardian_utils import is_superuser
from library.utils import delimited_row, ExportRow, export_column
from snpdb.models import VariantAllele, allele_flag_types, GenomeBuild, Variant
from snpdb.models.models_variant import Allele
from snpdb.views.datatable_view import DatatableConfig, RichColumn, SortOrder


def _alleles_with_classifications_qs() -> QuerySet[Allele]:
    """
    Only consider alleles that have variant classifications
    as there are way too many alleles to consider otherwise
    """
    classification_variant_ids_qs = Classification.objects.exclude(withdrawn=True).values_list('variant__id', flat=True)
    allele_ids = VariantAllele.objects.filter(variant_id__in=classification_variant_ids_qs).values_list('allele_id', flat=True)
    return Allele.objects.filter(id__in=allele_ids)


@user_passes_test(is_superuser)
def view_hgvs_issues(request: HttpRequest) -> Response:

    alleles_qs = _alleles_with_classifications_qs().order_by('-id')
    allele_missing_rep_qs = FlagCollection.filter_for_open_flags(qs=alleles_qs, flag_types=[allele_flag_types.missing_37, allele_flag_types.missing_38])

    allele_missing_clingen = alleles_qs.filter(clingen_allele__isnull=True)
    allele_37_not_38 = FlagCollection.filter_for_open_flags(qs=alleles_qs, flag_types=[allele_flag_types.allele_37_not_38])

    vcqs = Classification.objects.filter(withdrawn=False)
    matching_variant = FlagCollection.filter_for_open_flags(qs=vcqs, flag_types=[classification_flag_types.matching_variant_flag])
    matching_variant_warning = FlagCollection.filter_for_open_flags(qs=vcqs, flag_types=[classification_flag_types.matching_variant_warning_flag])
    matching_variant_transcript = FlagCollection.filter_for_open_flags(qs=vcqs, flag_types=[classification_flag_types.transcript_version_change_flag])

    issue_counts = {
        "allele": {
            "missing_rep": allele_missing_rep_qs.count(),
            "missing_clingen": allele_missing_clingen.count(),
            "chgvs_37_not_38": allele_37_not_38.count()
        },
        "classifications": {
            "matching_variant": matching_variant.count(),
            "matching_variant_warning": matching_variant_warning.count(),
            "matching_variant_transcript": matching_variant_transcript.count()
        }
    }
    context = {
        "counts": issue_counts
    }

    return render(request, "classification/hgvs_issues.html", context)


class AlleleColumns(DatatableConfig):

    def get_allele(self, allele_id: int) -> Allele:
        if last_allele := self.last_allele:
            if last_allele.id == allele_id:
                return last_allele
        last_allele = Allele.objects.get(id=allele_id)
        return last_allele

    def variant_for(self, row: Dict[str, Any], genome_build: GenomeBuild) -> str:
        values = list()
        allele = self.get_allele(row["id"])
        variant: Variant
        try:
            variant = allele.variant_for_build(genome_build=genome_build, best_attempt=False)
        except ValueError:
            return "-"
        values.append(f'<span class="text-secondary">{variant}</span>')
        if variant_annotation := variant.get_best_variant_transcript_annotation(genome_build):
            if gene := variant_annotation.gene:
                gene_symbol = gene.get_gene_symbol(genome_build)
                values.append(gene_symbol.symbol)

        return "<br/>".join(values)

    def variant_37(self, row: Dict[str, Any]) -> Optional[str]:
        return self.variant_for(row, GenomeBuild.grch37())

    def variant_38(self, row: Dict[str, Any]) -> Optional[str]:
        return self.variant_for(row, GenomeBuild.grch38())

    def __init__(self, request):
        super().__init__(request)
        self.last_allele: Optional[Allele] = None

        self.rich_columns = [
            RichColumn(key="id", label='ID', client_renderer='alleleIdRender', orderable=True, default_sort=SortOrder.DESC),
            RichColumn(key="clingen_allele__id", client_renderer='clingenIdRenderer', label='ClinGen Allele', orderable=True),
            RichColumn(name="variant_37", label='37 Variant', renderer=self.variant_37, orderable=False),
            RichColumn(name="variant_38", label='38 Variant', renderer=self.variant_38, orderable=False),
            RichColumn(key="flag_collection_id", label="Flags", client_renderer='TableFormat.flags')
        ]

    def get_initial_queryset(self):
        # exclude where we've auto matched and have 0 outstanding left
        return _alleles_with_classifications_qs()

    def filter_queryset(self, qs: QuerySet) -> QuerySet:
        if flag_filter := self.get_query_param('flag'):
            if flag_filter == 'missing_rep':
                qs = FlagCollection.filter_for_open_flags(qs=qs, flag_types=[allele_flag_types.missing_37,
                                                                             allele_flag_types.missing_38])
            elif flag_filter == 'missing_clingen':
                qs = qs.filter(clingen_allele__isnull=True)
            elif flag_filter == 'chgvs_37_not_38':
                qs = FlagCollection.filter_for_open_flags(qs=qs, flag_types=[allele_flag_types.allele_37_not_38])

        return qs


@dataclass
class HgvsIssuesRow(ExportRow):
    allele: Optional[Allele] = None
    classification: Optional[Classification] = None
    flag: Optional[Flag] = None

    @export_column("Allele ID")
    def allele_id(self) -> Optional[str]:
        if allele := self.allele:
            return str(allele.id)

    @export_column("Allele URL")
    def allele_url(self) -> Optional[str]:
        if allele := self.allele:
            return get_url_from_view_path(allele.get_absolute_url())

    @export_column("ClinGen Allele ID")
    def clingen_allele_id(self) -> Optional[str]:
        if allele := self.allele:
            return allele.clingen_allele_id

    @export_column("Best Transcript Gene")
    def allele_gene_symbol(self) -> Optional[str]:
        if allele := self.allele:
            for genome_build in [GenomeBuild.grch37(), GenomeBuild.grch38()]:
                try:
                    variant = self.allele.variant_for_build(genome_build, best_attempt=False)
                    if variant_annotation := variant.get_best_variant_transcript_annotation(genome_build):
                        if gene := variant_annotation.gene:
                            if gene_symbol := gene.get_gene_symbol(genome_build):
                                return gene_symbol.symbol
                except ValueError:
                    pass

    @export_column("Allele GRCh37")
    def allele_grch37(self) -> Optional[str]:
        if allele := self.allele:
            return str(allele.grch37)

    @export_column("Allele GRCh38")
    def allele_grch38(self) -> Optional[str]:
        if allele := self.allele:
            return str(allele.grch38)

    @export_column("Classification URL")
    def classification_url(self):
        if classification := self.classification:
            return get_url_from_view_path(classification.get_absolute_url())

    @export_column("Classification GRCh37")
    def classification_37(self):
        if classification := self.classification:
            return classification.chgvs_grch37

    @export_column("Classification GRCh38")
    def classification_38(self):
        if classification := self.classification:
            return classification.chgvs_grch38

    @export_column("Issue Type")
    def issue_type(self):
        if flag := self.flag:
            return flag.flag_type.label

    @export_column("Issue Text")
    def issue_text(self):
        if flag := self.flag:
            return flag.flagcomment_set.first().text


@dataclass(frozen=True)
class ProblemHgvs(ExportRow):
    classification: Classification

    def flag_formatter(self, flag_type: FlagType, data: Dict[str, Any] = None):
        qs: QuerySet[Flag]
        if flag_type.context_id == 'classification':
            qs = self.classification.flags_of_type(flag_type=flag_type)
        elif flag_type.context_id == 'allele':
            if allele := self.allele:
                qs = allele.flags_of_type(flag_type=flag_type)
            else:
                return
        else:
            raise ValueError(f"Unexpected flag context {flag_type.context_id}")

        qs = qs.order_by('-created')
        if data:
            for key, value in data.items():
                qs = qs.filter(**{f'data__{key}': value})

        if last_flag := qs.first():
            last_comment: FlagComment = last_flag.flagcomment_set.order_by('-created').first()
            closed = last_flag.resolution.status == FlagStatus.CLOSED
            if closed:
                return f"Closed : {last_comment.user.username}"
            else:
                return "Open"

    @lazy
    def allele(self):
        if variant := self.classification.variant:
            return variant.allele

    @export_column("Classification URL")
    def classification_url(self):
        return get_url_from_view_path(self.classification.get_absolute_url())

    @export_column("Imported Build")
    def imported_build(self):
        return self.classification.get(SpecialEKeys.GENOME_BUILD)

    @export_column("Imported 37")
    def imported_c_hgvs_37(self):
        if (imported_build := self.imported_build()) and '37' in imported_build:
            return self.classification.get(SpecialEKeys.C_HGVS)

    @export_column("Resolved 37")
    def resolved_37(self):
        return self.classification.chgvs_grch37

    @export_column("Imported 38")
    def imported_c_hgvs_38(self):
        if (imported_build := self.imported_build()) and '38' in imported_build:
            return self.classification.get(SpecialEKeys.C_HGVS)

    @export_column("Resolved 38")
    def resolved_38(self):
        return self.classification.chgvs_grch38

    @export_column("Flag Matching")
    def flag_variant_matching(self):
        return self.flag_formatter(classification_flag_types.matching_variant_flag)

    @export_column("Flag Matching Warning")
    def flag_matching_warning(self):
        return self.flag_formatter(classification_flag_types.matching_variant_warning_flag)

    @export_column("Transcript Change")
    def flag_transcript_change(self):
        return self.flag_formatter(classification_flag_types.transcript_version_change_flag)

    @export_column("Allele URL")
    def allele_url(self):
        if allele := self.allele:
            return get_url_from_view_path(allele.get_absolute_url())

    @export_column("37 != 38")
    def flag_37_not_38(self):
        return self.flag_formatter(allele_flag_types.allele_37_not_38, data={"transcript": self.classification.transcript})

    @export_column("!37")
    def flag_37(self):
        return self.flag_formatter(allele_flag_types.missing_37)

    @export_column("!38")
    def flag_38(self):
        return self.flag_formatter(allele_flag_types.missing_38)


@user_passes_test(is_superuser)
def download_hgvs_issues(request: HttpRequest) -> StreamingHttpResponse:

    # source data as all classifications with a flag
    # and all classifications attached to an allele with a flag
    alleles_qs = FlagCollection.filter_for_flags(Allele.objects.all())
    classification_qs = FlagCollection.filter_for_flags(Classification.objects.all(), flag_types=[
        classification_flag_types.matching_variant_warning_flag,
        classification_flag_types.transcript_version_change_flag,
        classification_flag_types.matching_variant_flag
    ])
    complete_qs = classification_qs.union(Classification.objects.filter(variant__variantallele__allele__in=alleles_qs))
    complete_qs = complete_qs.order_by('-variant', '-pk')

    return ProblemHgvs.streaming_csv(complete_qs, "hgvs_issues")

# @user_passes_test(is_superuser)
# def download_hgvs_issues(request: HttpRequest) -> StreamingHttpResponse:
#
#     def row_generator() -> Iterable[str]:
#         yield delimited_row(HgvsIssuesRow.csv_header())
#         alleles_qs = FlagCollection.filter_for_open_flags(qs=_alleles_with_classifications_qs())
#         for allele in alleles_qs:
#             open_flags = Flag.objects.filter(collection=allele.flag_collection).filter(FlagCollection.Q_OPEN_FLAGS)
#             for flag in open_flags:
#                 yield delimited_row(HgvsIssuesRow(allele=allele, flag=flag).to_csv())
#
#         classification_hgvs_issue_flag_types = [
#             classification_flag_types.matching_variant_flag,
#             classification_flag_types.matching_variant_warning_flag,
#             classification_flag_types.transcript_version_change_flag
#         ]
#         classification_qs = FlagCollection.filter_for_open_flags(qs=Classification.objects.all(), flag_types=classification_hgvs_issue_flag_types)
#         for classification in classification_qs:
#             open_flags = Flag.objects.filter(collection=classification.flag_collection).filter(FlagCollection.Q_OPEN_FLAGS).filter(flag_type__in=classification_hgvs_issue_flag_types)
#             for flag in open_flags:
#                 allele = classification.variant.allele if classification.variant else None
#                 yield delimited_row(HgvsIssuesRow(allele=allele, classification=classification, flag=flag).to_csv())
#
#     response = StreamingHttpResponse(row_generator(), content_type='text/csv')
#     response['Content-Disposition'] = f'attachment; filename="allele_issues_{now().astimezone(tz=timezone(settings.TIME_ZONE)).strftime("%Y-%m-%d")}.csv"'
#     return response

