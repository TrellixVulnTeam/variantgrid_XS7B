# Generated by Django 3.1 on 2020-09-29 06:10

from django.db import migrations


def genelist_categories(apps, schema_editor):
    CATEGORIES = ["CustomText",
                  "PathologyTest",
                  "NodeCustomText",
                  "SampleGeneList",
                  "Uploaded"]

    GeneListCategory = apps.get_model("genes", "GeneListCategory")
    for c in CATEGORIES:
        GeneListCategory.objects.get_or_create(name=c)


def initial_gene_info(apps, schema_editor):
    GeneInfo = apps.get_model("genes", "GeneInfo")
    GeneListCategory = apps.get_model("genes", "GeneListCategory")
    GENE_INFO_NAME = "GeneInfo"

    category, created = GeneListCategory.objects.get_or_create(name=GENE_INFO_NAME)
    if created:
        #category.hidden = True
        category.description = "Special category to hold gene info (ie tag genes)"
        category.save()

    GENE_INFO = [
        ("Alternative Haplotype", "alt-haplotype-icon"),
        ("Pseudogene", "pseudogene-icon"),
        ("Triplet Repeat Disorders", "triplet-repeat-icon"),
    ]

    for name, icon_css_class in GENE_INFO:
        GeneInfo.objects.create(name=name, description="", icon_css_class=icon_css_class)


class Migration(migrations.Migration):

    dependencies = [
        ('genes', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(genelist_categories),
        migrations.RunPython(initial_gene_info),
    ]
