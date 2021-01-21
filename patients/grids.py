from django.contrib.postgres.aggregates.general import StringAgg
from django.db.models.aggregates import Count
from django.db.models.query_utils import Q
from django.shortcuts import get_object_or_404

from annotation.models.models_phenotype_match import PATIENT_GENE_SYMBOL_PATH, PATIENT_ONTOLOGY_TERM_PATH
from library.django_utils import get_model_fields
from library.jqgrid_user_row_config import JqGridUserRowConfig
from ontology.models import OntologyTerm
from patients.models import PatientRecords, Patient, PatientRecord


class PatientListGrid(JqGridUserRowConfig):
    model = Patient
    caption = 'Patients'
    fields = ["id", "external_pk__code", "family_code", "phenotype", "modified", "affected", "consanguineous"]
    colmodel_overrides = {'id': {'width': 20, 'formatter': 'viewPatientLink'}}

    def __init__(self, **kwargs):
        user = kwargs.get("user")
        extra_filters = kwargs.pop("extra_filters", {})
        super().__init__(user)
        queryset = Patient.filter_for_user(user)
        if extra_filters:
            term_type = extra_filters["term_type"]
            value = extra_filters["value"]

            # We need to filter to a sub patients list NOT just to certain terms, so that StringAgg will
            # return all the terms for that person
            if term_type == 'ontology_term':
                ontology_term = OntologyTerm.get_from_slug(value)
                patient_id_q = Q(**{PATIENT_ONTOLOGY_TERM_PATH: ontology_term})
            elif term_type == 'gene':
                # Match to gene_symbol as there may be multiple with that symbol
                patient_id_q = Q(**{PATIENT_GENE_SYMBOL_PATH: value})
            else:
                msg = f"Unknown term type '{term_type}'"
                raise ValueError(msg)

            patient_id_qs = Patient.objects.filter(patient_id_q).values_list("pk", flat=True)
            queryset = queryset.filter(pk__in=patient_id_qs)

        # Add sample_count to queryset
        annotation_kwargs = {"reference_id": StringAgg("specimen__reference_id", ',', distinct=True),
                             "ontology_terms": StringAgg(PATIENT_ONTOLOGY_TERM_PATH + "__name", '|', distinct=True),
                             "genes": StringAgg(PATIENT_GENE_SYMBOL_PATH, '|', distinct=True),
                             "sample_count": Count("sample", distinct=True),
                             "samples": StringAgg("sample__name", ", ", distinct=True)}
        queryset = queryset.annotate(**annotation_kwargs)
        field_names = self.get_field_names() + list(annotation_kwargs.keys())
        self.queryset = queryset.values(*field_names)

        self.extra_config.update({'sortname': 'modified',
                                  'sortorder': 'desc'})

    def get_colmodels(self, remove_server_side_only=False):
        colmodels = super().get_colmodels(remove_server_side_only=remove_server_side_only)
        EXTRA_COLUMNS = [
            {'index': 'reference_id', 'name': 'reference_id', 'label': 'Specimen ReferenceIDs'},
            {'index': 'ontology_terms', 'name': 'ontology_terms', 'label': 'Ontology Terms', 'classes': 'no-word-wrap'},
            {'index': 'genes', 'name': 'genes', 'label': 'Genes', 'classes': 'no-word-wrap', 'formatter': 'geneFormatter'},
            {'index': 'sample_count', 'name': 'sample_count', 'label': '# samples', 'sorttype': 'int', 'width': '30px'},
            {'index': 'samples', 'name': 'samples', 'label': 'Samples'},
        ]
        colmodels.extend(EXTRA_COLUMNS)
        return colmodels


class PatientRecordsGrid(JqGridUserRowConfig):
    model = PatientRecords
    caption = 'PatientRecords'
    fields = ["id", "uploadedpatientrecords__uploaded_file__user__username", "uploadedpatientrecords__uploaded_file__name"]
    colmodel_overrides = {'id': {'width': 40, 'formatter': 'viewPatientRecordsLink'},
                          'uploadedpatientrecords__uploaded_file__user__username': {'label': 'Uploaded by'},
                          'uploadedpatientrecords__uploaded_file__name': {'label': 'Uploaded File Name'}}

    def __init__(self, **kwargs):
        user = kwargs.get("user")
        super().__init__(user)
        queryset = self.model.objects.filter(uploadedpatientrecords__uploaded_file__user=user)
        self.queryset = queryset.values(*self.get_field_names())
        self.extra_config.update({'sortname': 'id',
                                  'sortorder': 'desc'})


class PatientRecordGrid(JqGridUserRowConfig):
    model = PatientRecord
    caption = 'PatientRecord'
    fields = get_model_fields(PatientRecord)

    def __init__(self, **kwargs):
        user = kwargs.get("user")
        patient_records_id = kwargs.pop('patient_records_id')
        super().__init__(user)

        patient_records = get_object_or_404(PatientRecords, pk=patient_records_id)
        patient_records.uploaded_file.check_can_view(user)
        queryset = self.model.objects.filter(patient_records=patient_records)
        self.queryset = queryset.values(*self.get_field_names())
        self.extra_config.update({'sortname': 'id',
                                  'sortorder': 'desc'})
