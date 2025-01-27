import abc

from django.db.models.functions.text import Length
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

from genes.models import PanelAppPanel, GeneList, GeneSymbol, Gene, Transcript, GeneAnnotationRelease, PanelAppServer
from library.constants import HOUR_SECS, WEEK_SECS, MINUTE_SECS
from library.django_utils.autocomplete_utils import AutocompleteView


class AbstractPanelAppPanelAutocompleteView(abc.ABC, AutocompleteView):
    fields = ['name']

    @abc.abstractmethod
    def _get_server(self):
        pass

    def get_user_queryset(self, user):
        qs = PanelAppPanel.objects.all()
        if server := self._get_server():
            qs = qs.filter(server=server)
        return qs


@method_decorator(cache_page(HOUR_SECS), name='dispatch')
class PanelAppPanelAutocompleteView(AbstractPanelAppPanelAutocompleteView):
    def _get_server(self):
        # Passed server_id in forward
        server = None
        if server_id := self.forwarded.get('server_id', None):
            server = PanelAppServer.objects.get(pk=server_id)
        return server


@method_decorator(cache_page(HOUR_SECS), name='dispatch')
class PanelAppPanelAusAutocompleteView(AbstractPanelAppPanelAutocompleteView):
    def _get_server(self):
        return PanelAppServer.australia_instance()


@method_decorator(cache_page(HOUR_SECS), name='dispatch')
class PanelAppPanelEngAutocompleteView(AbstractPanelAppPanelAutocompleteView):
    def _get_server(self):
        return PanelAppServer.england_instance()


@method_decorator(cache_page(WEEK_SECS), name='dispatch')
class GeneAutocompleteView(AutocompleteView):
    fields = ['geneversion__gene_symbol__symbol']

    def sort_queryset(self, qs):
        f = "geneversion__gene_symbol__symbol"
        return qs.order_by(Length(f).asc(), f)

    def get_user_queryset(self, user):
        annotation_consortium = self.forwarded.get('annotation_consortium', None)
        qs = Gene.objects.all().distinct()

        if annotation_consortium:
            qs = qs.filter(annotation_consortium=annotation_consortium)
        return qs


@method_decorator(cache_page(WEEK_SECS), name='dispatch')
class TranscriptAutocompleteView(AutocompleteView):
    fields = ['identifier']

    def sort_queryset(self, qs):
        f = "identifier"
        return qs.order_by(Length(f).asc(), f)

    def get_user_queryset(self, user):
        gene = self.forwarded.get('gene', None)
        genome_build = self.forwarded.get('genome_build', None)
        qs = Transcript.objects.all().distinct()

        if gene:
            qs = qs.filter(transcriptversion__gene_version__gene=gene)
        if genome_build:
            qs = qs.filter(transcriptversion__genome_build=genome_build)
        return qs


@method_decorator(cache_page(WEEK_SECS), name='dispatch')
class GeneSymbolAutocompleteView(AutocompleteView):
    fields = ['symbol']

    def sort_queryset(self, qs):
        return qs.order_by(Length("symbol").asc(), 'symbol')

    def get_user_queryset(self, _user):
        """ Doesn't actually use user for genes """
        qs = GeneSymbol.objects.all()
        if self.q:
            qs = qs.filter(symbol__istartswith=self.q)
        return qs


@method_decorator(cache_page(WEEK_SECS), name='dispatch')
class GeneAnnotationReleaseAutocompleteView(AutocompleteView):
    fields = ['version', 'genome_build__name']

    def get_user_queryset(self, _user):
        """ Doesn't actually use user for GeneAnnotationRelease """
        qs = GeneAnnotationRelease.objects.all()
        if genome_build_id := self.forwarded.get('genome_build_id', None):
            qs = qs.filter(genome_build_id=genome_build_id)
        return qs


@method_decorator([cache_page(MINUTE_SECS), vary_on_cookie], name='dispatch')
class GeneListAutocompleteView(AutocompleteView):
    fields = ['name']

    def get_user_queryset(self, user):
        return GeneList.filter_for_user(user)


#@method_decorator([cache_page(MINUTE_SECS), vary_on_cookie], name='dispatch')
class CategoryGeneListAutocompleteView(AutocompleteView):
    fields = ['name']

    def get_user_queryset(self, user):
        category = self.forwarded.get('category', None)
        qs = GeneList.filter_for_user(user)
        if category:
            qs = qs.filter(category=category)
        else:
            qs = qs.filter(category__isnull=True)
        return qs
