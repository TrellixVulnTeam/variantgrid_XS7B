from rest_framework import serializers

from genes.models import GeneInfo, GeneListCategory, GeneList, Gene, Transcript, GeneListGeneSymbol, \
    GeneAnnotationRelease, SampleGeneList, ActiveSampleGeneList, GeneSymbol, TranscriptVersion, GeneVersion, HGNC
from snpdb.models import Company
from snpdb.serializers import UserSerializer, GenomeBuildSerializer


class GeneSymbolSerializer(serializers.ModelSerializer):

    class Meta:
        model = GeneSymbol
        fields = ('symbol', )


class GeneSerializer(serializers.ModelSerializer):

    class Meta:
        model = Gene
        fields = ('identifier', )


class GeneVersionSerializer(serializers.ModelSerializer):
    gene = GeneSerializer()
    gene_symbol = GeneSymbolSerializer()
    genome_build = GenomeBuildSerializer()

    class Meta:
        model = GeneVersion
        fields = ('gene', 'version', 'gene_symbol', 'genome_build')


class TranscriptSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transcript
        fields = ('identifier', )


class TranscriptVersionSerializer(serializers.ModelSerializer):
    transcript = TranscriptSerializer()
    genome_build = GenomeBuildSerializer()
    gene_version = GeneVersionSerializer()

    class Meta:
        model = TranscriptVersion
        fields = ('transcript', 'version', 'genome_build', 'gene_version')


class HGNCSerializer(serializers.ModelSerializer):
    gene_symbol = GeneSymbolSerializer()
    status = serializers.SerializerMethodField()

    class Meta:
        model = HGNC
        fields = ('hgnc_id', 'gene_symbol', 'approved_name', 'status')

    def get_status(self, obj: HGNC):
        return obj.get_status_display()


class GeneListCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = GeneListCategory
        fields = ('name', 'public', 'company', 'icon_css_class', 'description')


class GeneListGeneSymbolSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneListGeneSymbol
        fields = ('original_name', 'gene_symbol', 'gene_symbol_alias', 'modification_info')


class GeneListSerializer(serializers.ModelSerializer):
    category = GeneListCategorySerializer()
    user = UserSerializer()
    genelistgenesymbol_set = GeneListGeneSymbolSerializer(many=True)
    can_write = serializers.SerializerMethodField()
    absolute_url = serializers.URLField(source='get_absolute_url', read_only=True)

    class Meta:
        model = GeneList
        fields = ('pk', 'category', 'name', 'user', 'import_status', 'genelistgenesymbol_set', 'can_write', 'absolute_url')

    def get_can_write(self, obj: GeneList):
        user = self.context['request'].user

        if obj.id:  # Can't check pk as may be FakeGeneList object
            can_write = obj.can_write(user)
        else:
            # Not yet saved, so no permissions etc
            can_write = user == obj.user

        if can_write and obj.category and obj.category.company:
            company = Company.get_our_company()
            if obj.category.company != company:
                can_write = False

        return can_write


class GeneAnnotationReleaseSerializer(serializers.ModelSerializer):
    __str__ = serializers.SerializerMethodField()

    class Meta:
        model = GeneAnnotationRelease
        fields = ("version", "annotation_consortium", "genome_build", "__str__")

    def get___str__(self, obj):
        return str(obj)


class GeneInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = GeneInfo
        fields = ('name', 'description', 'icon_css_class')


class SampleGeneListSerializer(serializers.ModelSerializer):
    active = serializers.SerializerMethodField()

    class Meta:
        model = SampleGeneList
        fields = ('pk', 'visible', 'active')

    def get_active(self, obj):
        try:
            return obj.sample.activesamplegenelist.sample_gene_list == obj
        except ActiveSampleGeneList.DoesNotExist:
            return False
