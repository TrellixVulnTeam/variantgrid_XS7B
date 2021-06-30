# Generated by Django 3.1.3 on 2021-06-30 05:53

from django.db import migrations


def variantgrid_column_full_paths(apps, schema_editor):
    VariantGridColumn = apps.get_model("snpdb", "VariantGridColumn")
    # Also need to rename filternodes to new columns
    FilterNodeItem = apps.get_model("analysis", "FilterNodeItem")

    # Use full path rather than ForeignKey so we know the type, to be able to adjust JQGrid filter settings
    COLUMN_CHANGES = {
        'clingen_allele': 'variantallele__allele__clingen_allele__id',
        'gene_id': 'variantannotation__gene__identifier',
        'uniprot_id': 'variantannotation__uniprot__accession',
    }

    for grid_column_name, variant_column in COLUMN_CHANGES.items():
        vgc = VariantGridColumn.objects.get(grid_column_name=grid_column_name)
        old_column = vgc.variant_column
        vgc.variant_column = variant_column
        vgc.save()

        num_changed = FilterNodeItem.objects.filter(field=old_column).update(field=variant_column)
        print(f"Renamed {num_changed} FilterNodeItems from '{old_column}' => '{old_column}'")

    # Also need to update FilterNode old vs new?


class Migration(migrations.Migration):

    dependencies = [
        ('snpdb', '0035_merge_20210520_1246'),
    ]

    operations = [
        migrations.RunPython(variantgrid_column_full_paths),
    ]
