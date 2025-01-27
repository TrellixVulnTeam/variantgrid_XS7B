# Generated by Django 4.0.2 on 2022-05-02 03:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('annotation', '0047_remove_humanproteinatlasannotation_abundance_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            """
            DO $$
            DECLARE
                tables CURSOR FOR
                    SELECT tablename
                    FROM pg_tables
                    WHERE tablename LIKE 'annotation_variantannotation_version_%'
                    ORDER BY tablename;
            BEGIN
                FOR table_record IN tables LOOP
                EXECUTE format('ALTER TABLE %I 
                DROP COLUMN IF EXISTS "cadd_raw",
                DROP COLUMN IF EXISTS "fathmm_pred",
                DROP COLUMN IF EXISTS "gene_text",
                DROP COLUMN IF EXISTS "hgnc_id",
                DROP COLUMN IF EXISTS "mutation_assessor_pred",
                DROP COLUMN IF EXISTS "mutation_taster_pred",
                DROP COLUMN IF EXISTS "polyphen2_hvar_pred",
                DROP COLUMN IF EXISTS "swissprot",
                DROP COLUMN IF EXISTS "symbol_source",
                DROP COLUMN IF EXISTS "trembl",
                DROP COLUMN IF EXISTS "uniparc";', table_record.tablename);
                END LOOP;
            END$$;
            
            
            DO $$
            DECLARE
                tables CURSOR FOR
                    SELECT tablename
                    FROM pg_tables
                    WHERE tablename LIKE 'annotation_varianttranscriptannotation_version_%'
                    ORDER BY tablename;
            BEGIN
                FOR table_record IN tables LOOP
                EXECUTE format('ALTER TABLE %I 
                DROP COLUMN IF EXISTS "cadd_raw",
                DROP COLUMN IF EXISTS "dbsnp_rs_id",
                DROP COLUMN IF EXISTS "fathmm_pred",
                DROP COLUMN IF EXISTS "gene_text",
                DROP COLUMN IF EXISTS "hgnc_id",
                DROP COLUMN IF EXISTS "mutation_assessor_pred",
                DROP COLUMN IF EXISTS "mutation_taster_pred",
                DROP COLUMN IF EXISTS "phastcons_100_way_vertebrate",
                DROP COLUMN IF EXISTS "phastcons_30_way_mammalian",
                DROP COLUMN IF EXISTS "phastcons_46_way_mammalian",
                DROP COLUMN IF EXISTS "phylop_100_way_vertebrate",
                DROP COLUMN IF EXISTS "phylop_30_way_mammalian",
                DROP COLUMN IF EXISTS "phylop_46_way_mammalian",
                DROP COLUMN IF EXISTS "polyphen2_hvar_pred",
                DROP COLUMN IF EXISTS "pubmed",
                DROP COLUMN IF EXISTS "swissprot",
                DROP COLUMN IF EXISTS "symbol_source",
                DROP COLUMN IF EXISTS "trembl",
                DROP COLUMN IF EXISTS "uniparc",
                DROP COLUMN IF EXISTS "predictions_num_benign",
                DROP COLUMN IF EXISTS "predictions_num_pathogenic";', table_record.tablename);
                END LOOP;
            END$$;
            """
        )
    ]
