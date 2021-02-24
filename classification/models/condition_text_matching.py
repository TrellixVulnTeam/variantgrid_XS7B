import operator
from dataclasses import dataclass
from functools import reduce
from typing import List, Optional, Dict, Any, Iterable, Set

import requests
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db.models import CASCADE, QuerySet, SET_NULL, Q
from django.dispatch import receiver
from guardian.shortcuts import assign_perm
from lazy import lazy
from model_utils.models import TimeStampedModel
from django.db import models, transaction
from classification.enums import SpecialEKeys, ShareLevel
from classification.models import Classification, ClassificationModification, classification_post_publish_signal, \
    flag_types, EvidenceKeyMap
from classification.regexes import db_ref_regexes, DbRegexes
from flags.models import flag_comment_action, Flag, FlagComment, FlagResolution
from genes.models import GeneSymbol
from library.django_utils.guardian_permissions_mixin import GuardianPermissionsMixin
from library.guardian_utils import admin_bot
from library.log_utils import report_exc_info
from library.utils import ArrayLength
from ontology.models import OntologyTerm, OntologyService, OntologySnake, OntologyTermRelation
from ontology.ontology_matching import OntologyMatching, normalize_condition_text, \
    OPRPHAN_OMIM_TERMS, SearchText, pretty_set, PREFIX_SKIP_TERMS
from ontology.panel_app_ontology import update_gene_relations
from snpdb.models import Lab


class ConditionText(TimeStampedModel, GuardianPermissionsMixin):
    normalized_text = models.TextField()
    lab = models.ForeignKey(Lab, on_delete=CASCADE, null=True, blank=True)

    classifications_count = models.IntegerField(default=0)
    classifications_count_outstanding = models.IntegerField(default=0)

    class Meta:
        unique_together = ("normalized_text", "lab")

    @staticmethod
    def normalize(text: str):
        return normalize_condition_text(text)

    def __str__(self):
        return self.normalized_text

    # TODO is this better done as an before save hook?
    def save(self, **kwargs):

        super().save(**kwargs)
        assign_perm(self.get_read_perm(), self.lab.group, self)
        assign_perm(self.get_write_perm(), self.lab.group, self)

    @transaction.atomic
    def clear(self):
        self.conditiontextmatch_set.update(condition_xrefs=list(), condition_multi_operation=MultiCondition.NOT_DECIDED, last_edited_by=None)
        self.classifications_count_outstanding = self.classifications_count
        self.save()

    @property
    def classification_match_count(self) -> int:
        return self.classifications_count - self.classifications_count_outstanding

    @property
    def user_edited(self) -> bool:
        return self.conditiontextmatch_set.annotate(condition_xrefs_length=ArrayLength('condition_xrefs')).filter(condition_xrefs_length__gt=0).exclude(last_edited_by=admin_bot()).exists()

    @property
    def root(self) -> 'ConditionTextMatch':
        return self.conditiontextmatch_set.filter(gene_symbol__isnull=True, mode_of_inheritance__isnull=True, classification=None).first()

    @property
    def gene_levels(self) -> Iterable['ConditionTextMatch']:
        return self.conditiontextmatch_set.filter(condition_text=self, gene_symbol__isnull=False, mode_of_inheritance__isnull=True, classification=None)


class MultiCondition(models.TextChoices):
    NOT_DECIDED = 'N', 'Not decided'
    UNCERTAIN = 'U', 'Uncertain'  # aka uncertain
    CO_OCCURRING = 'C', 'Co-occurring'  # aka combined


class ResolvedCondition:

    def __init__(self, search_term: Optional[str], gene_symbol: Optional[str]):
        self.condition_multi_operation = MultiCondition.NOT_DECIDED
        self.condition_xrefs = OntologyMatching(search_term=search_term, gene_symbol=gene_symbol)


class ConditionTextMatch(TimeStampedModel, GuardianPermissionsMixin):
    condition_text = models.ForeignKey(ConditionText, on_delete=CASCADE)
    last_edited_by = models.ForeignKey(User, on_delete=SET_NULL, null=True, blank=True)

    parent = models.ForeignKey('ConditionTextMatch', on_delete=CASCADE, null=True, blank=True)
    gene_symbol = models.ForeignKey(GeneSymbol, on_delete=CASCADE, null=True, blank=True)
    mode_of_inheritance = ArrayField(models.TextField(blank=False), default=None, null=True, blank=True)
    classification = models.OneToOneField(Classification, on_delete=CASCADE, null=True, blank=True)

    @property
    def name(self):
        if self.classification:
            return self.classification.friendly_label
        if self.mode_of_inheritance:
            e_key = EvidenceKeyMap.cached_key(SpecialEKeys.MODE_OF_INHERITANCE)
            return e_key.pretty_value(self.mode_of_inheritance)
        if self.gene_symbol:
            return self.gene_symbol.symbol
        return "Default"

    def get_permission_object(self):
        return self.condition_text

    @classmethod
    def get_permission_class(cls):
        return ConditionText

    @property
    def hierarchy(self) -> List[Any]:
        h_list = list()
        if self.gene_symbol:
            h_list.append(self.gene_symbol)
        if self.mode_of_inheritance is not None:
            h_list.append(self.mode_of_inheritance)
        if self.classification:
            h_list.append(self.classification)
        return h_list

    @property
    def is_root(self):
        return not self.gene_symbol

    @property
    def is_gene_level(self):
        # just used for templates
        return not self.classification_id and self.mode_of_inheritance is None and self.gene_symbol_id is not None

    @property
    def is_classification_level(self):
        return self.classification_id

    @lazy
    def classification_count(self):
        if self.classification_id:
            return 1
        elif self.mode_of_inheritance:
            return self.condition_text.conditiontextmatch_set.filter(parent=self).count()
        elif self.gene_symbol_id:
            return self.condition_text.conditiontextmatch_set.filter(classification_id__isnull=False, gene_symbol__pk=self.gene_symbol_id).count()
        else:
            return self.condition_text.conditiontextmatch_set.filter(classification_id__isnull=False).count()

    @property
    def leaf(self) -> Optional[Any]:
        if self.classification:
            return self.classification
        elif self.mode_of_inheritance is not None:
            return self.mode_of_inheritance
        elif self.gene_symbol:
            return self.gene_symbol
        else:
            return None

    # resolved to this,
    condition_xrefs = ArrayField(models.TextField(blank=False), default=list)
    condition_multi_operation = models.CharField(max_length=1, choices=MultiCondition.choices, default=MultiCondition.NOT_DECIDED)

    @lazy
    def resolve_condition_xrefs(self) -> Optional[ResolvedCondition]:
        """
        Return the effective terms for this element
        If no terms have been set for this match, check the parent match
        """
        if not self.condition_xrefs:
            if not self.parent:
                return None
            else:
                return self.parent.resolve_condition_xrefs

        rc = ResolvedCondition(search_term=None, gene_symbol=None)
        rc.condition_multi_operation = self.condition_multi_operation
        for term in self.condition_xrefs:
            rc.condition_xrefs.select_term(term)
        return rc

    @property
    def condition_matching_str(self) -> str:
        """
        Produce a single efficient line on what this condition text match is, e.g.
        MONDO:00001233; MONDO:0553533; co-occurring
        """
        result = ''
        if self.condition_xrefs:
            result = ", ".join(self.condition_xrefs)
        if len(self.condition_xrefs) >= 2:
            if self.condition_multi_operation == MultiCondition.NOT_DECIDED:
                result += "; uncertain/co-occurring"
            elif self.condition_multi_operation == MultiCondition.CO_OCCURRING:
                result += "; co-occurring"
            elif self.condition_multi_operation == MultiCondition.UNCERTAIN:
                result += "; uncertain"
        return result

    def update_with_condition_matching_str(self, text: str):
        """
        Update teh condition text match with a single line of text e.g.
        MONDO:00001233; MONDO:0553533; co-occurring
        So the inverse of condition_matching_str
        """
        terms = list()
        condition_multi_operation = MultiCondition.NOT_DECIDED

        parts = text.split(";")
        if len(parts) >= 1:
            terms_part = parts[0]
            # this way we only recognise ids we recognise
            # but do we want that?
            # also allows us to fix the length of ids
            # also allows us to fix the length of ids

            # also assume any dangling number is a mondo term?
            db_refs = db_ref_regexes.search(terms_part, default_regex=DbRegexes.MONDO)
            terms = [db_ref.id_fixed for db_ref in db_refs]
        if len(parts) >= 2:
            operation_part = parts[1].lower()
            if '/' in operation_part:
                condition_multi_operation = MultiCondition.NOT_DECIDED
            elif 'co' in operation_part:
                condition_multi_operation = MultiCondition.CO_OCCURRING
            elif 'un' in operation_part:
                condition_multi_operation = MultiCondition.UNCERTAIN

        self.condition_xrefs = terms
        self.condition_multi_operation = condition_multi_operation

    class Meta:
        unique_together = ("condition_text", "gene_symbol", "mode_of_inheritance", "classification")

    @property
    def is_valid(self):
        return len(self.condition_xrefs) == 1 or \
               (len(self.condition_xrefs) > 1 and self.condition_multi_operation != MultiCondition.NOT_DECIDED)

    @lazy
    def condition_xref_terms(self) -> List[OntologyTerm]:
        terms = list()
        for term_str in self.condition_xrefs:
            try:
                terms.append(OntologyTerm.get_or_stub(term_str))
            except ValueError:
                pass
        return terms

    @property
    def is_blank(self):
        return len(self.condition_xrefs) == 0

    @lazy
    def children(self) -> QuerySet:
        order_by: str
        if self.is_root:
            order_by = 'gene_symbol__symbol'
        elif self.is_gene_level:
            order_by = 'mode_of_inheritance'
        else:
            order_by = 'classification__id'

        return self.conditiontextmatch_set.all().order_by(order_by)

    @staticmethod
    def sync_all():
        """
        syncs ConditionTextMatch's to Classifications
        """
        cms = ClassificationModification.objects.filter(is_last_published=True, classification__withdrawn=False).select_related("classification", "classification__lab")
        cm: ClassificationModification
        for cm in cms:
            ConditionTextMatch.sync_condition_text_classification(cm=cm, update_counts=False)

        for ct in ConditionText.objects.all():
            ConditionTextMatch.attempt_automatch(condition_text=ct)
            update_condition_text_match_counts(ct)
            if ct.classifications_count == 0:
                ct.delete()
            else:
                ct.save()

    @staticmethod
    def attempt_automatch(condition_text: ConditionText):
        try:
            if root := condition_text.root:
                if match := top_level_suggestion(condition_text.normalized_text):
                    if match.is_auto_assignable() and not root.condition_xrefs:
                        print(f"{condition_text.root} : {match.terms}")
                        root.condition_xrefs = match.term_str_array
                        root.last_edited_by = admin_bot()
                        root.save()
                    else:
                        for gene_symbol_level in condition_text.gene_levels:
                            if match.is_auto_assignable(gene_symbol=gene_symbol_level.gene_symbol) and not gene_symbol_level.condition_xrefs:
                                print(f"{condition_text.root} {gene_symbol_level.gene_symbol} : {match.terms}")
                                gene_symbol_level.condition_xrefs = match.term_str_array
                                gene_symbol_level.last_edited_by = admin_bot()
                                gene_symbol_level.save()
        except Exception:
            report_exc_info()

    @staticmethod
    def sync_condition_text_classification(cm: ClassificationModification, update_counts=True, attempt_automatch=False):
        classification = cm.classification
        if classification.withdrawn:
            ConditionTextMatch.objects.filter(classification=classification).delete()
            return

        lab = classification.lab
        gene_str = cm.get(SpecialEKeys.GENE_SYMBOL)
        gene_symbol = GeneSymbol.objects.filter(symbol=gene_str).first()

        existing: ConditionTextMatch = ConditionTextMatch.objects.filter(classification=classification).first()

        if not gene_symbol or classification.withdrawn:
            if existing:
                ct = existing.condition_text
                existing.delete()
                if update_counts:
                    update_condition_text_match_counts(ct)
            return
        else:
            raw_condition_text = cm.get(SpecialEKeys.CONDITION) or ""
            normalized = ConditionText.normalize(raw_condition_text)

            # need mode_of_inheritance to be not null
            mode_of_inheritance = cm.get(SpecialEKeys.MODE_OF_INHERITANCE) or []

            ct: ConditionText
            ct, ct_is_new = ConditionText.objects.get_or_create(normalized_text=normalized, lab=lab)

            # if condition text has changed, remove the old entries
            ConditionTextMatch.objects.filter(classification=classification).exclude(condition_text=ct).delete()

            root, new_root = ConditionTextMatch.objects.get_or_create(
                condition_text=ct,
                gene_symbol=None,
                mode_of_inheritance=None,
                classification=None
            )

            gene_level, new_gene_level = ConditionTextMatch.objects.get_or_create(
                parent=root,
                condition_text=ct,
                gene_symbol=gene_symbol,
                mode_of_inheritance=None,
                classification=None
            )

            mode_of_inheritance_level, _ = ConditionTextMatch.objects.get_or_create(
                parent=gene_level,
                condition_text=ct,
                gene_symbol=gene_symbol,
                mode_of_inheritance=mode_of_inheritance,
                classification=None
            )

            if existing:
                if existing.parent != mode_of_inheritance_level or \
                        existing.condition_text != ct or \
                        existing.gene_symbol != gene_symbol or \
                        existing.mode_of_inheritance != mode_of_inheritance:

                    # update existing to new hierarchy
                    # assume if a condition has been set for this classification specifically that it's
                    # still valid
                    old_text = existing.condition_text
                    existing.parent = mode_of_inheritance_level
                    existing.condition_text = ct
                    existing.mode_of_inheritance = mode_of_inheritance
                    existing.save()

                    update_condition_text_match_counts(old_text)
                    old_text.save()
                else:
                    # nothing has changed, no need to update anything
                    return
            else:
                ConditionTextMatch.objects.create(
                    parent=mode_of_inheritance_level,
                    condition_text=ct,
                    gene_symbol=gene_symbol,
                    mode_of_inheritance=mode_of_inheritance,
                    classification=classification
                )

            save_required = False
            if attempt_automatch and (new_root or new_gene_level):
                ConditionTextMatch.attempt_automatch(ct)
                save_required = True

            if update_counts:
                update_condition_text_match_counts(ct)
                save_required = True

            if save_required:
                ct.save()


def update_condition_text_match_counts(ct: ConditionText):
    # let's us count by doing one select all of the database, rather than continually
    # selecting parents from the DB
    by_id: Dict[int, ConditionTextMatch] = dict()
    classification_related: List[ConditionTextMatch] = list()
    for ctm in ct.conditiontextmatch_set.all():
        by_id[ctm.id] = ctm
        if ctm.classification:
            classification_related.append(ctm)

    def check_hierarchy(ctm: ConditionTextMatch) -> bool:
        if ctm.is_valid:
            return True
        elif not ctm.is_blank:
            return False
        else:
            if parent := by_id.get(ctm.parent_id):
                return check_hierarchy(parent)
            return False

    invalid_count = 0
    for ctm in classification_related:
        if not check_hierarchy(ctm):
            invalid_count += 1

    ct.classifications_count = len(classification_related)
    ct.classifications_count_outstanding = invalid_count


@dataclass
class ConditionMatchingMessage:
    severity: str
    text: str

    def as_json(self):
        return {
            "severity": self.severity,
            "text": self.text
        }


class ConditionMatchingSuggestion:

    def __init__(self, condition_text_match: Optional[ConditionTextMatch] = None, ignore_existing: bool = False):
        self.condition_text_match = condition_text_match
        self.terms: List[OntologyTerm] = condition_text_match.condition_xref_terms if condition_text_match and not ignore_existing else []
        self.is_applied = bool(self.terms)
        self.hidden = False
        self.condition_multi_operation: MultiCondition = MultiCondition.NOT_DECIDED
        if self.is_applied:
            self.condition_multi_operation = condition_text_match.condition_multi_operation
        self.messages: List[ConditionMatchingMessage] = list()
        self.validated = False
        self.ids_found_in_text: Optional[bool] = None
        self.alias_index: Optional[int] = None

    @property
    def term_str_array(self) -> List[str]:
        return [term.id for term in self.terms]

    def add_term(self, term: OntologyTerm):
        if term not in self.terms:
            self.terms.append(term)

    def add_message(self, message: ConditionMatchingMessage):
        self.messages.append(message)

    def as_json(self):
        user_json = None
        if self.terms and self.is_applied: # only report on user who filled in values
            if condition_text_match := self.condition_text_match:
                if user := condition_text_match.last_edited_by:
                    user_json = {"username": user.username}

        return {
            "id": self.condition_text_match.id if self.condition_text_match else None,
            "is_applied": self.is_applied,
            "hidden": self.hidden,
            "terms": [{"id": term.id, "name": term.name, "definition": '???' if term.is_stub else term.definition} for term in self.terms],
            "joiner": self.condition_multi_operation,
            "messages": [message.as_json() for message in self.messages],
            "user": user_json
        }

    def is_auto_assignable(self, gene_symbol: Optional[GeneSymbol] = None):
        # FIXME need to know if was assigned via embedded terms or not
        if terms := self.terms:
            if len(terms) != 1:
                return False
            for message in self.messages:
                if message.severity not in {"success", "info"}:
                    return False

            if gene_symbol:
                if self.is_all_leafs():
                    # if we're at a gene level, and we have a relationship and we're leafs
                    term = terms[0]
                    if OntologySnake.gene_symbols_for_term(term).filter(pk=gene_symbol.pk).exists():
                        return True
            else:
                # embedded ID is the only thing that will give you a top level assignment
                if self.ids_found_in_text:
                    return True
        return False

    def validate(self):
        if self.validated:
            return
        else:
            self.validated = True
        if terms := self.terms:
            # validate if we have multiple terms without a valid joiner
            if len(terms) > 1 and self.condition_multi_operation not in {MultiCondition.UNCERTAIN,
                                                                        MultiCondition.CO_OCCURRING}:
                self.add_message(ConditionMatchingMessage(severity="error",
                                                         text="Multiple terms provided, requires co-occurring/uncertain"))

            if valid_terms := [term for term in terms if not term.is_stub]:
                ontology_services: Set[str] = set()
                for term in valid_terms:
                    ontology_services.add(term.ontology_service)
                if len(ontology_services) > 1:
                    self.add_message(ConditionMatchingMessage(severity="error",
                                                             text=f"Only one ontology type is supported per level, {' and '.join(ontology_services)} found"))

                # validate that the terms have a known gene association if we're at gene level
                if ctm := self.condition_text_match:
                    if ctm.is_gene_level:
                        gene_symbol = self.condition_text_match.gene_symbol
                        update_gene_relations(gene_symbol)
                        for term in valid_terms:
                            if not OntologySnake.gene_symbols_for_term(term).filter(pk=gene_symbol.pk).exists():
                                self.add_message(ConditionMatchingMessage(severity="warning",
                                                                         text=f"{term.id} : no direct relationship on file to {gene_symbol.symbol}"))
                            else:
                                self.add_message(ConditionMatchingMessage(severity="success",
                                                                         text=f"{term.id} : has a relationship to {gene_symbol.symbol}"))

            # validate that we have the terms being referenced (if we don't big chance that they're not valid)
            for term in terms:
                if term.is_stub:
                    self.add_message(ConditionMatchingMessage(severity="warning",
                                                             text=f"{term.id} : no copy of this term in our system"))
                elif term.is_obsolete:
                    self.add_message(
                        ConditionMatchingMessage(severity="error", text=f"{term.id} : is marked as obsolete"))

    def is_all_leafs(self):
        if terms := self.terms:
            for term in terms:
                if not term.is_leaf:
                    return False
            return True
        return None

    def __bool__(self):
        return not not self.terms or not not self.messages


@receiver(classification_post_publish_signal, sender=Classification)
def published(sender,
              classification: Classification,
              previously_published: ClassificationModification,
              newly_published: ClassificationModification,
              previous_share_level: ShareLevel,
              user: User,
              **kwargs):
    """
    Keeps condition_text_match in sync with the classifications when evidence changes
    """
    ConditionTextMatch.sync_condition_text_classification(newly_published, attempt_automatch=True, update_counts=True)


@receiver(flag_comment_action, sender=Flag)
def check_for_discordance(sender, flag_comment: FlagComment, old_resolution: FlagResolution, **kwargs):
    """
    Keeps condition_text_match in sync with the classifications when withdraws happen/finish
    """
    flag = flag_comment.flag
    if flag.flag_type == flag_types.classification_flag_types.classification_withdrawn:
        cl: Classification
        if cl := Classification.objects.filter(flag_collection=flag.collection.id).first():
            ConditionTextMatch.sync_condition_text_classification(cl.last_published_version, attempt_automatch=True, update_counts=True)


def top_level_suggestion(text: str) -> ConditionMatchingSuggestion:
    if suggestion := embedded_ids_check(text):
        return suggestion
    return search_suggestion(text)


def embedded_ids_check(text: str) -> ConditionMatchingSuggestion:
    cms = ConditionMatchingSuggestion()

    db_matches = db_ref_regexes.search(text)
    detected_any_ids = bool(db_matches)  # see if we found any prefix suffix, if we do,
    db_matches = [match for match in db_matches if match.db in ["OMIM", "HP", "MONDO"]]

    for match in db_matches:
        cms.add_term(OntologyTerm.get_or_stub(match.id_fixed))

    found_stray_omim = False

    # fall back to looking for stray OMIM terms if we haven't found any ids e.g. PMID:123456 should stop this code
    if not detected_any_ids:
        stray_omim_matches = OPRPHAN_OMIM_TERMS.findall(text)
        stray_omim_matches = [term for term in stray_omim_matches if len(term) == 6]
        if stray_omim_matches:
            for omim_index in stray_omim_matches:
                omim = OntologyTerm.get_or_stub(f"OMIM:{omim_index}")
                cms.add_term(omim)
                cms.add_message(ConditionMatchingMessage(severity="warning", text=f"OMIM:{omim_index} was found without a prefix"))

    if cms.terms:
        cms.ids_found_in_text = True
        if len(cms.terms) == 1:
            matched_term = cms.terms[0]
            text_tokens = SearchText.tokenize_condition_text(normalize_condition_text(text), deplural=True, deroman=True)
            term_tokens = SearchText.tokenize_condition_text(normalize_condition_text(matched_term.name), deplural=True, deroman=True)
            if aliases := matched_term.aliases:
                for alias in aliases:
                    term_tokens = term_tokens.union(SearchText.tokenize_condition_text(normalize_condition_text(alias), deplural=True, deroman=True))
            term_tokens.add(str(matched_term.id).lower())
            term_tokens.add(str(matched_term.id.split(":")[1]))
            extra_words = text_tokens.difference(term_tokens) - PREFIX_SKIP_TERMS
            if len(extra_words) >= 3:
                cms.add_message(ConditionMatchingMessage(severity="warning", text=f"Found {matched_term.id} in text, but also apparently unrelated words : {pretty_set(extra_words)}"))

    cms.validate()
    return cms


def search_text_to_suggestion(search_text: SearchText, term: OntologyTerm) -> ConditionMatchingSuggestion:
    cms = ConditionMatchingSuggestion()
    if match_info := search_text.matches(term):
        if match_info.alias_index is not None:  # 0 alias is complete with acronymn, 1 alias without acronymn
            safe_alias = False
            if term.ontology_service == OntologyService.OMIM:
                alias = term.aliases[match_info.alias_index]
                if alias in [name_part.strip() for name_part in term.name.split(";")]:
                    # alias is part one of the name parts, would barely refer to it as an alias
                    safe_alias = True
            if not safe_alias:
                cms.add_message(ConditionMatchingMessage(severity="warning", text=f"Text matched on alias of {term.id}"))
                cms.alias_index = match_info.alias_index
        if term.ontology_service == OntologyService.OMIM:
            if mondo := OntologyTermRelation.as_mondo(term):
                cms.add_message(ConditionMatchingMessage(severity="warning", text=f"Converted from OMIM term {term.id}"))
                term = mondo
            else:
                # slowly direct users to MONDO
                cms.add_message(ConditionMatchingMessage(severity="warning", text="Matched on OMIM, please attempt to find MONDO term if possible"))

        cms.add_term(term)
        cms.validate()
        return cms
    return cms


def find_local_term(match_text: SearchText, service: OntologyService) -> Optional[ConditionMatchingSuggestion]:
    q = list()
    # TODO, can we leverage phenotype matching?
    if match_text.prefix_terms:
        term_list = list(match_text.prefix_terms)
        if len(term_list) == 1 and len(term_list[0]) <= 4:
            term_str: str = term_list[0]
            # check array contains (and hope we don't have any mixed case aliases)
            q.append(Q(name__iexact=term_str) | Q(aliases__contains=[term_str.upper()]) | Q(
                aliases__contains=[term_str.lower()]))
        else:
            for term_str in term_list:
                if len(term_str) > 1:
                    # problem with icontains in aliases is it converts array list to a string, and then finds text in there
                    # so "hamper,laundry" would be returned for icontains="ham"
                    q.append(Q(name__icontains=term_str) | Q(aliases__icontains=term_str))

    matches = list()
    if q:
        for term in OntologyTerm.objects.filter(ontology_service=service).filter(reduce(
                operator.and_, q)).order_by('ontology_service')[0:200]:
            if cms := search_text_to_suggestion(match_text, term):
                matches.append(cms)
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        if name_matches := [match for match in matches if match.alias_index is None]:
            if len(name_matches) == 1:
                return name_matches[0]
    return None


def search_suggestion(text: str) -> ConditionMatchingSuggestion:
    match_text = SearchText(text)
    if local_mondo := find_local_term(match_text, OntologyService.MONDO):
        return local_mondo

    try:
        # TODO ensure "text" is safe, it should already be normalised
        results = requests.get(
            f'https://api.monarchinitiative.org/api/search/entity/autocomplete/{text}', {
                "prefix": "MONDO",
                "rows": 10,
                "minimal_tokenizer": "false",
                "category": "disease"
            }).json().get("docs")

        for result in results:
            o_id = result.get('id')
            # result.get('label') gives the label as it's known by the search server
            term = OntologyTerm.get_or_stub(o_id)
            if cms := search_text_to_suggestion(match_text, term):
                return cms
    except:
        print("Error searching server")

    if local_omim := find_local_term(match_text, OntologyService.OMIM):
        return local_omim

    return ConditionMatchingSuggestion()


def is_descendant(terms: Set[OntologyTerm], ancestors: Set[OntologyTerm], seen: Set[OntologyTerm], check_levels: int = 10):
    # TODO move this to OntologyTerm class
    for term in terms:
        if term in ancestors:
            return True
    if check_levels == 0:
        return False

    all_parent_terms = set()
    for term in terms:
        if parents := OntologyTermRelation.parents_of(term):
            for parent in parents:
                if parent not in seen:
                    all_parent_terms.add(parent)
    if all_parent_terms:
        seen = seen.union(all_parent_terms)
        return is_descendant(all_parent_terms, ancestors, seen, check_levels-1)


def condition_matching_suggestions(ct: ConditionText, ignore_existing=False) -> List[ConditionMatchingSuggestion]:
    suggestions = list()

    root_level = ct.root
    root_cms: Optional[ConditionMatchingSuggestion]

    root_cms = ConditionMatchingSuggestion(root_level, ignore_existing=ignore_existing)
    is_root_real: bool
    display_root_cms = root_cms
    if root_cms.terms:
        is_root_real = True
    else:
        root_cms = top_level_suggestion(ct.normalized_text)
        root_cms.condition_text_match = root_level
        if root_cms.ids_found_in_text:
            display_root_cms = root_cms
            is_root_real = True
        else:
            is_root_real = False

    root_cms.validate()
    suggestions.append(display_root_cms)

    # filled in and gene level, exclude root as we take care of that before-hand
    filled_in: QuerySet
    filled_in = ct.conditiontextmatch_set.annotate(condition_xrefs_length=ArrayLength('condition_xrefs')).filter(Q(condition_xrefs_length__gt=0) | Q(parent=root_level)).exclude(gene_symbol=None)

    for ctm in filled_in:
        if ctm.condition_xref_terms and not ignore_existing:
            cms = ConditionMatchingSuggestion(ctm)
            cms.validate()
            suggestions.append(cms)

        elif ctm.is_gene_level:  # should be the only other option
            # chances are we'll have some suggestions or warnings for gene level if we have root level
            # if we don't no foul, we just send down an empty context
            # and if we got rid of root level, might need to blank out gene level suggestions/warnings
            cms = ConditionMatchingSuggestion(condition_text_match=ctm, ignore_existing=ignore_existing)
            suggestions.append(cms)

            gene_symbol = ctm.gene_symbol
            if root_level_terms := root_cms.terms:  # uses suggestions and selected values

                if root_level_mondo := set([term for term in root_level_terms if term.ontology_service == OntologyService.MONDO]):
                    gene_level_terms = set(OntologySnake.terms_for_gene_symbol(gene_symbol=gene_symbol, desired_ontology=OntologyService.MONDO).leafs())
                    matches_gene_level = set()
                    for gene_level in gene_level_terms:
                        if is_descendant({gene_level}, root_level_mondo, set()):
                            matches_gene_level.add(gene_level)

                    matches_gene_level_leafs = [term for term in matches_gene_level if term.is_leaf]
                    root_level_str = ', '.join([term.id for term in root_level_mondo])

                    if not matches_gene_level:
                        cms.add_message(ConditionMatchingMessage(severity="warning", text=f"{root_level_str} : Could not find relationship to {gene_symbol}"))
                    elif len(matches_gene_level) == 1:
                        term = list(matches_gene_level)[0]
                        if term in root_level_terms:
                            cms.add_message(ConditionMatchingMessage(severity="success",
                                                                     text=f"{term.id} : has a relationship to {gene_symbol.symbol}"))
                        else:
                            cms.add_message(ConditionMatchingMessage(severity="success",
                                                                 text=f"{term.id} : has a relationship to {gene_symbol.symbol}"))
                            cms.add_term(list(matches_gene_level)[0])  # not guaranteed to be a leaf, but no associations on child terms
                    elif len(matches_gene_level_leafs) == 1:
                        term = list(matches_gene_level_leafs)[0]
                        cms.add_message(ConditionMatchingMessage(severity="success",
                                                                 text=f"{term.id} : has a relationship to {gene_symbol.symbol}"))
                        cms.add_term(matches_gene_level_leafs[0])
                    else:
                        cms.add_message(ConditionMatchingMessage(severity="warning", text=f"{root_level_str} : Multiple children of this term are associated to {gene_symbol}"))

                else:
                    # if not MONDO term, see if this term has a known relationship directly
                    parent_term_missing_gene = list()
                    parent_term_has_gene = list()
                    for term in root_level_terms:
                        if not OntologySnake.gene_symbols_for_term(term).filter(pk=gene_symbol.pk).exists():
                            parent_term_missing_gene.append(term)
                        else:
                            parent_term_has_gene.append(term)

                    for term in parent_term_missing_gene:
                        cms.add_message(ConditionMatchingMessage(severity="warning", text=f"{term.id} : no relationship on file to {gene_symbol.symbol}"))
                    for term in parent_term_has_gene:
                        cms.add_message(ConditionMatchingMessage(severity="success",
                                                                 text=f"{term.id} : has a relationship to {gene_symbol.symbol}"))

                if cms.terms == root_cms.terms and root_cms.ids_found_in_text:
                    cms.terms = []  # no need to duplicate when ids found in text

                if not cms.terms:
                    if root_cms.is_applied:
                        # if parent was applied, and all we have are warnings
                        # put them in the applied column not suggestion
                        cms.is_applied = True
                    else:
                        # if root was a suggestion, but we couldn't come up with a more specific suggestion
                        # suggest the root at each gene level anyway (along with any warnings we may have generated)
                        if not root_cms.ids_found_in_text:
                            cms.terms = root_cms.terms  # just copy parent term if couldn't use child term
                            for message in root_cms.messages:
                                cms.add_message(message)
                        pass

    return suggestions