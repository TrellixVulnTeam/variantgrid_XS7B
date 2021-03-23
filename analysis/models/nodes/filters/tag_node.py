from typing import List

from django.contrib.auth.models import User
from django.db import models
from django.db.models.deletion import SET_NULL, CASCADE
from django.db.models.query_utils import Q
from django_extensions.db.models import TimeStampedModel
from lazy import lazy

from analysis.models.enums import TagNodeMode
from analysis.models.nodes.analysis_node import Analysis, AnalysisNode
from annotation.annotation_version_querysets import get_variant_queryset_for_latest_annotation_version
from snpdb.models import Tag, Variant, GenomeBuild, VariantAllele


class TagNode(AnalysisNode):
    ANALYSIS_TAGS_NAME = "Tagged Variants"
    mode = models.CharField(max_length=1, choices=TagNodeMode.choices, default=TagNodeMode.PARENT)

    def modifies_parents(self):
        return True

    @lazy
    def tag_ids(self) -> List[str]:
        # This is called when Node is being initialised to set the name
        if self.pk is None:
            return []

        qs = Tag.objects.filter(tagnodetag__tag_node=self).order_by("id").values_list("id", flat=True)
        return list(qs)

    def _get_node_q(self) -> Q:
        if self.mode == TagNodeMode.ALL_ANALYSES:
            analyses = Analysis.filter_for_user(self.analysis.user)
        else:
            analyses = [self.analysis]

        variants_qs = VariantTag.variants_for_build(self.analysis.genome_build, analyses, self.tag_ids)
        return Q(pk__in=list(variants_qs.values_list("pk", flat=True)))

    def get_node_name(self):
        if self.visible:
            if self.tag_ids:
                description = f"Tagged {', '.join(self.tag_ids)}"
            else:
                description = "All Tags"
        else:
            description = self.ANALYSIS_TAGS_NAME  # Has to be set to this

        return description

    def save_clone(self):
        tag_ids = self.tag_ids  # Save before clone
        copy = super().save_clone()
        for tag_id in tag_ids:
            copy.tagnodetag_set.create(tag_id=tag_id)
        return copy

    @staticmethod
    def get_node_class_label():
        return "Tags"

    def _get_method_summary(self):
        return f"Tagged {', '.join(self.tag_ids)} ({self.get_mode_display()})"

    def get_css_classes(self):
        css_classes = super().get_css_classes()
        if self.tag_ids:
            css_classes.extend([f"tagged-{tag_id}" for tag_id in self.tag_ids])
        return css_classes

    @property
    def min_inputs(self):
        return self.max_inputs

    @property
    def max_inputs(self):
        if self.mode == TagNodeMode.PARENT:
            return 1
        return 0

    @staticmethod
    def get_analysis_tags_node(analysis):
        from analysis.tasks.node_update_tasks import update_node_task

        node, created = TagNode.objects.get_or_create(analysis=analysis,
                                                      name=TagNode.ANALYSIS_TAGS_NAME,
                                                      mode=TagNodeMode.THIS_ANALYSIS,
                                                      visible=False)
        if created:
            # Should be fast, so do sync (not as celery job)
            update_node_task(node.pk, node.version)
        return node


class TagNodeTag(models.Model):
    """ Stores multi-select values """
    tag_node = models.ForeignKey(TagNode, on_delete=CASCADE)
    tag = models.ForeignKey(Tag, null=True, blank=True, on_delete=SET_NULL)

    class Meta:
        unique_together = ("tag_node", "tag")


class VariantTag(TimeStampedModel):
    """ A tag in an analysis. Has create create/delete signal handlers:
        @see analysis.signals.signal_handlers._update_analysis_on_variant_tag_change """
    variant = models.ForeignKey(Variant, on_delete=CASCADE)
    tag = models.ForeignKey(Tag, on_delete=CASCADE)
    analysis = models.ForeignKey(Analysis, on_delete=CASCADE)
    # Most recent node where it was added
    node = models.ForeignKey(AnalysisNode, null=True, on_delete=SET_NULL)  # Keep even if node deleted
    user = models.ForeignKey(User, on_delete=CASCADE)

    def can_write(self, user):
        return self.analysis.can_write(user)

    @staticmethod
    def get_for_build(genome_build: GenomeBuild, variant_qs=None):
        """ Returns tags visible within a build
            variant_qs - set to filter - default (None) = all variants """
        va_kwargs = {
            "genome_build": genome_build,
            "allele__in": VariantTag.objects.all().values_list("variant__variantallele__allele")
        }
        if variant_qs is not None:
            va_kwargs["variant__in"] = variant_qs

        va_qs = VariantAllele.objects.filter(**va_kwargs)
        return VariantTag.objects.filter(variant__variantallele__allele__in=va_qs.values_list("allele", flat=True))

    @staticmethod
    def variants_for_build(genome_build, analyses, tag_ids: List[str]):
        tags_qs = VariantTag.get_for_build(genome_build).filter(analysis__in=analyses)
        if tag_ids:
            tags_qs = tags_qs.filter(tag__in=tag_ids)

        qs = get_variant_queryset_for_latest_annotation_version(genome_build)
        return qs.filter(variantallele__genome_build=genome_build,
                         variantallele__allele__in=tags_qs.values_list("variant__variantallele__allele", flat=True))
