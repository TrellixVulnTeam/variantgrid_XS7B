# Generated by Django 3.2.4 on 2021-09-06 04:34
# compare_chgvs needs to be able to tell if HGVSs have changed (allele_37_not_38) and to update it
# To do this, Flag.data has to have changed, and thus we need to store the c_hgvs in it
# See variantgrid_private issue #3132
import re

from django.db import migrations
from django.db.models import Q


def _one_off_allele_37_not_38_data(apps, schema_editor):
    Flag = apps.get_model("flags", "Flag")
    FlagType = apps.get_model("flags", "FlagType")
    FLAG_STATUS_OPEN = 'O'

    allele_37_not_38 = FlagType.objects.get(pk='allele_37_not_38')

    for flag in Flag.objects.filter(flag_type=allele_37_not_38, resolution__status=FLAG_STATUS_OPEN):
        contains_both = Q(text__contains='GRCh37') & Q(text__contains='GRCh38')
        if comment := flag.flagcomment_set.filter(contains_both, resolution__id='open').order_by("modified").last():
            c_hgvs_by_build = {}
            for line in comment.text.split("\n"):
                if m := re.match(r"(.*) \((GRCh37|GRCh38)\)", line):
                    c_hgvs, build_name = m.groups()
                    c_hgvs_by_build[build_name] = c_hgvs

            if len(c_hgvs_by_build) == 2:
                flag.data["chgvs37"] = c_hgvs_by_build["GRCh37"]
                flag.data["chgvs38"] = c_hgvs_by_build["GRCh38"]
                flag.save()


class Migration(migrations.Migration):

    dependencies = [
        ('flags', '0003_rename_variant_classification'),
    ]

    operations = [
        migrations.RunPython(_one_off_allele_37_not_38_data)
    ]
