# Generated by Django 4.0.2 on 2022-02-16 23:11

from django.db import migrations


def _one_off_proband_het_to_sample(apps, schema_editor):
    TrioNode = apps.get_model("analysis", "TrioNode")
    SampleNode = apps.get_model("analysis", "SampleNode")
    NodeVersion = apps.get_model("analysis", "NodeVersion")
    NodeVCFFilter = apps.get_model("analysis", "NodeVCFFilter")
    NodeAlleleFrequencyFilter = apps.get_model("analysis", "NodeAlleleFrequencyFilter")
    AnalysisEdge = apps.get_model("analysis", "AnalysisEdge")
    VariantTag = apps.get_model("analysis", "VariantTag")
    AnalysisVariable = apps.get_model("analysis", "AnalysisVariable")

    PROBAND_HET = 'P'
    for old_node in TrioNode.objects.filter(inheritance=PROBAND_HET):
        sample = None
        if old_node.trio:
            sample = old_node.trio.proband.sample
        new_node = SampleNode.objects.create(analysis=old_node.analysis,
                                             name='Proband HET',
                                             sample=sample,
                                             status=old_node.status, count=old_node.count,
                                             x=old_node.x, y=old_node.y,
                                             min_ad=old_node.min_ad,
                                             min_dp=old_node.min_dp,
                                             min_gq=old_node.min_gq,
                                             max_pl=old_node.max_pl,
                                             zygosity_ref=False,
                                             zygosity_het=True,
                                             zygosity_hom=False,
                                             zygosity_unk=False)

        node_version = NodeVersion.objects.get_or_create(node=new_node, version=new_node.version)[0]
        # Node counts

        old_node_version = NodeVersion.objects.filter(node=old_node, version=old_node.version).first()
        if old_node_version:
            for node_count in old_node_version.nodecount_set.all():
                node_count.pk = None
                node_count.node_version = node_version
                node_count.save()

        for npf in NodeVCFFilter.objects.filter(node=old_node):
            npf.pk = None
            npf.node = new_node
            npf.save()

        naff = NodeAlleleFrequencyFilter.objects.filter(node=old_node).first()  # 1-to-1
        if naff:
            af_frequency_ranges = list(naff.nodeallelefrequencyrange_set.all().values_list("min", "max"))
            # Use existing if already created for node (eg AlleleFrequencyNode always makes one)
            copy_naff, created = NodeAlleleFrequencyFilter.objects.get_or_create(node=new_node)
            if not created:
                # Wipe out defaults to clear way for clone
                copy_naff.nodeallelefrequencyrange_set.all().delete()
            copy_naff.group_operation = naff.group_operation
            copy_naff.save()

            for min_value, max_value in af_frequency_ranges:
                copy_naff.nodeallelefrequencyrange_set.create(min=min_value, max=max_value)

        # Swap out children
        AnalysisEdge.objects.filter(parent=old_node).update(parent=new_node)
        VariantTag.objects.filter(node=old_node).update(node=new_node)

        # If it has analysis variable - need to also copy that
        for av in AnalysisVariable.objects.filter(node=old_node):
            if not (av.field == 'trio' or av.class_name == ''):
                msg = f"Don't know how to handle {av.node_id} analysis variable of '{av.field}'/'{av.class_name}'"
                raise ValueError(msg)
            av.node = new_node
            av.field = 'sample'
            av.class_name = 'snpdb.Sample'
            av.save()

        print(old_node.delete())


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0060_remove_damagenode_allow_null_and_more'),
    ]

    operations = [
        migrations.RunPython(_one_off_proband_het_to_sample),
    ]
