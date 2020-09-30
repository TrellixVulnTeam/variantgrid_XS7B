from typing import List

from django.contrib.auth.models import User
from django.test import TestCase

from variantclassification.enums import SubmissionSource, \
    SpecialEKeys, ShareLevel
from variantclassification.models.tests.test_utils import VariantClassificationTestUtils
from variantclassification.models.variant_classification import VariantClassification, VariantClassificationModification
from variantclassification.models.variant_classification_patcher import patch_merge_age_units, patch_fuzzy_age
from variantclassification.models.variant_classification_utils import PatchMeta


class VariantClassificationTestCaseAge(TestCase):

    def setUp(self):
        VariantClassificationTestUtils.setUp()

    def tearDown(self):
        VariantClassificationTestUtils.tearDown()

    def test_patch_age(self):
        """
        age is a special case as we can get past age & age_units and want to merge them
        :return:
        """
        lab, user = VariantClassificationTestUtils.lab_and_user()
        user2 = User.objects.filter(username='joejoe2').get()
        vc = VariantClassification.create(
            user=user,
            lab=lab,
            lab_record_id=None,
            data={
                SpecialEKeys.C_HGVS: {'value': 'g.301A>C'},
                SpecialEKeys.G_HGVS: {'value': '5678'},
                'age': 17,
                'age_units': 'months'
            },
            save=True,
            source=SubmissionSource.API,
            make_fields_immutable=False
        )
        try:
            versions: List[VariantClassificationModification] = list()
            versions.append(vc.last_edited_version)

            vc.patch_value(patch={'age': 18}, user=user2, source=SubmissionSource.API, save=True)
            vc.publish_latest(user=user2, share_level=ShareLevel.INSTITUTION)
            versions.append(vc.last_edited_version)

            vc.patch_value(patch={'age_units': None}, user=user, source=SubmissionSource.API, save=True)
            versions.append(vc.last_edited_version)

            vc.patch_history(patch_merge_age_units)
            for version in versions:
                version.refresh_from_db()

            self.assertEqual(versions[2].previous, versions[1])
            self.assertEqual(versions[0].get('age'), '17months')
            self.assertEqual(versions[1].get('age'), '18months')
            self.assertEqual(versions[2].get('age'), '18')

            for version in versions:
                self.assertTrue(version.get('age_units') is None)

        finally:
            vc.delete()

    def test_patch_fuzzy_age(self):
        """
        Test converting age to a range of 10
        """
        lab, user = VariantClassificationTestUtils.lab_and_user()
        user2 = User.objects.filter(username='joejoe2').get()
        vc = VariantClassification.create(
            user=user,
            lab=lab,
            lab_record_id=None,
            data={
                SpecialEKeys.C_HGVS: {'value': 'g.301A>C'},
                SpecialEKeys.G_HGVS: {'value': '5678'},
                'age': 17,
                'age_units': 'months'
            },
            save=True,
            source=SubmissionSource.API,
            make_fields_immutable=False
        )
        try:
            versions: List[VariantClassificationModification] = list()
            versions.append(vc.last_edited_version)

            vc.patch_value(patch={'age': 18}, user=user2, source=SubmissionSource.API, save=True)
            vc.publish_latest(user=user2, share_level=ShareLevel.INSTITUTION)
            versions.append(vc.last_edited_version)

            # this below patch should have no effect
            vc.patch_value(patch={'age_units': None}, user=user, source=SubmissionSource.API, save=True)
            versions.append(vc.last_edited_version)

            vc.patch_value(patch={'age': 107}, user=user2, source=SubmissionSource.API, save=True)
            vc.publish_latest(user=user2, share_level=ShareLevel.INSTITUTION)
            versions.append(vc.last_edited_version)

            def age_conversion(patch: PatchMeta):
                patch_merge_age_units(patch)
                patch_fuzzy_age(patch)

            vc.patch_history(age_conversion)

            for version in versions:
                version.refresh_from_db()

            self.assertEqual(versions[0].get('age'), '0-9')
            self.assertEqual(versions[1].get('age'), '0-9')
            self.assertEqual(versions[2].get('age'), '10-19')
            self.assertEqual(versions[3].get('age'), '80+')

        finally:
            vc.delete()

    def test_age(self):
        patch = {
            SpecialEKeys.AGE: {"value": "90months"},
            SpecialEKeys.AGE_UNITS: {"value": "months"}
        }
        patch_meta = PatchMeta(patch=patch, existing={})

        patch_merge_age_units(patch_meta)
        patch_fuzzy_age(patch_meta)

        self.assertEqual(patch_meta.get('age'), '0-9')
