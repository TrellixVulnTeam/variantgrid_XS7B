from annotation.models.models_mim_hpo import MIMMorbid, HumanPhenotypeOntology


class HasPhenotypeDescriptionMixin:

    def _get_phenotype_input_text_field(self):
        """ Each subclass needs to implement - returns a string """
        raise NotImplementedError()

    def _get_phenotype_description_relation_class_and_kwargs(self):
        """ Each subclass needs to implement the way to get their PhenotypeDescription object """
        raise NotImplementedError()

    @property
    def phenotype_input_text(self):
        return getattr(self, self._get_phenotype_input_text_field())

    @phenotype_input_text.setter
    def phenotype_input_text(self, value):
        return setattr(self, self._get_phenotype_input_text_field(), value)

    @property
    def phenotype_description_relation(self):
        try:
            klass, kwargs = self._get_phenotype_description_relation_class_and_kwargs()
            _phenotype_description_relation = klass.objects.get(**kwargs)
        except:
            _phenotype_description_relation = None
        return _phenotype_description_relation

    @property
    def phenotype_description(self):
        if self.phenotype_description_relation:
            _phenotype_description = self.phenotype_description_relation.phenotype_description
        else:
            _phenotype_description = None
        return _phenotype_description

    def get_hpo_qs(self):
        if self.phenotype_description:
            hpos = self.phenotype_description.get_hpo_qs()
        else:
            hpos = HumanPhenotypeOntology.objects.none()  # @UndefinedVariable
        return hpos

    def get_mim_qs(self):
        if self.phenotype_description:
            mims = self.phenotype_description.get_mim_qs()
        else:
            mims = MIMMorbid.objects.none()
        return mims

    def get_mim_and_pheno_mim_qs(self):
        if self.phenotype_description:
            mims = self.phenotype_description.get_mim_and_pheno_mim_qs()
        else:
            mims = MIMMorbid.objects.none()
        return mims

    def get_gene_qs(self):
        from genes.models import Gene

        if self.phenotype_description:
            gene_qs = self.phenotype_description.get_gene_qs()
        else:
            gene_qs = Gene.objects.none()
        return gene_qs

    def process_phenotype_if_changed(self, lookup_factory=None, phenotype_approval_user=None):
        """ pass in lookup_factory to be able to cache it.
            if you don't pass in phenotype_approval_user assumed it is done automatically and thus needs user approval
            returns whether phenotype changed """

        # Stop circular import
        from annotation.phenotype_matching import default_lookup_factory, \
            create_phenotype_description
        if lookup_factory is None:
            lookup_factory = default_lookup_factory

        phenotype_input_text = self.phenotype_input_text
        phenotype_description_relation = self.phenotype_description_relation
        phenotype_description = None

        if phenotype_description_relation:
            phenotype_description = phenotype_description_relation.phenotype_description
            changed = phenotype_description and phenotype_description.original_text != phenotype_input_text
            if changed:
                phenotype_description.delete()
                phenotype_description = None
        else:
            klass, kwargs = self._get_phenotype_description_relation_class_and_kwargs()
            phenotype_description_relation = klass(**kwargs)  # Create a new one

        parsed_phenotypes = False
        if phenotype_input_text:
            if phenotype_description:  # Not deleted - so no change needed
                pass
            else:
                # TODO: Do as async job??
                phenotype_description_relation.phenotype_description = create_phenotype_description(phenotype_input_text, lookup_factory)
                phenotype_description_relation.approved_by = phenotype_approval_user
                phenotype_description_relation.save()

                parsed_phenotypes = True

        return parsed_phenotypes

    @staticmethod
    def pop_kwargs(kwargs_dict):
        """ remove kwargs (so save for other model does't fail """
        check_patient_text_phenotype = kwargs_dict.pop("check_patient_text_phenotype", True)
        phenotype_approval_user = kwargs_dict.pop("phenotype_approval_user", None)
        return {"check_patient_text_phenotype": check_patient_text_phenotype,
                "phenotype_approval_user": phenotype_approval_user}

    def save_phenotype(self, kwargs_dict):
        """ Pass kwargs_dict as dict - will pop fields it uses:
            "check_patient_text_phenotype" and "phenotype_approval_user" """

        kwargs = HasPhenotypeDescriptionMixin.pop_kwargs(kwargs_dict)
        check_patient_text_phenotype = kwargs["check_patient_text_phenotype"]
        phenotype_approval_user = kwargs["phenotype_approval_user"]

        # Some browsers send Text inputs with \r\n - while AJAX sends it as \n
        # strip \r to keep it consistent so that highlighting offsets line up
        if self.phenotype_input_text:
            self.phenotype_input_text = self.phenotype_input_text.replace('\r', '')

        if check_patient_text_phenotype:
            self.process_phenotype_if_changed(phenotype_approval_user=phenotype_approval_user)
