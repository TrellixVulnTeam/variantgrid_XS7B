from django.conf import settings
from django.db import models
from django.db.utils import ProgrammingError
from django.utils.text import slugify
import logging

from library.database_utils import run_sql
from library.log_utils import log_traceback
from library.utils import single_quote, double_quote


class RelatedModelsPartitionModel(models.Model):
    """ Partitions related model records by FK
        This should be inherited by the object that HOLDS the collection (that records point to)

        @see https://github.com/SACGF/variantgrid/wiki/Data-Partitioning """
    RECORDS_BASE_TABLE_NAMES = []
    RECORDS_FK_FIELD_TO_THIS_MODEL = None  # FK that points to this
    PARTITION_LABEL_TEXT = None  # Used to join between base_table_name and pk

    class Meta:
        abstract = True

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        created = not self.pk
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
        if created:
            self.create_partition()

    def create_partition(self):
        for base_table_name in self.RECORDS_BASE_TABLE_NAMES:
            self.create_partition_for_base_table(base_table_name)

    def create_partition_for_base_table(self, base_table_name):
        sql_template = """
    CREATE TABLE "%(table_name)s" (
        LIKE %(base_table_name)s including indexes,
        CHECK (%(records_fk_field)s = %(pk)s)
    ) INHERITS (%(base_table_name)s);
    """

        table_name = self.get_partition_table(base_table_name=base_table_name)
        logging.info("Creating Partition '%s'", table_name)
        pk = self.pk
        if isinstance(pk, str):
            pk = single_quote(pk)
        sql = sql_template % {"base_table_name": base_table_name,
                              "table_name": table_name,
                              "records_fk_field": self.RECORDS_FK_FIELD_TO_THIS_MODEL,
                              "pk": pk}
        run_sql(sql)

    def get_partition_table(self, base_table_name=None):
        if self.pk is None:
            msg = "Cannot set table as model is not saved"
            raise ValueError(msg)

        if base_table_name is not None:
            if base_table_name not in self.RECORDS_BASE_TABLE_NAMES:
                msg = f"get_partition_table(base_table_name={base_table_name}) not in RECORDS_BASE_TABLE_NAMES={self.RECORDS_BASE_TABLE_NAMES}"
                raise ValueError(msg)
        else:
            # Have to keep backwards compatibility
            if len(self.RECORDS_BASE_TABLE_NAMES) == 1:
                base_table_name = self.RECORDS_BASE_TABLE_NAMES[0]
            else:
                msg = f"get_partition_table() called with no argument, and >1 tables: {self.RECORDS_BASE_TABLE_NAMES}"
                raise ValueError(msg)

        return f"{base_table_name}_{self.PARTITION_LABEL_TEXT}_{slugify(self.pk)}"

    def sql_partition_transformer(self, sql):
        """' Modifies SQL generated by QuerySet
             @see library.django_utils.django_queryset_sql_transformer.get_queryset_with_transformer_hook  """

        for base_table_name in self.RECORDS_BASE_TABLE_NAMES:
            # Quote them, otherwise things can get replaced multiple times
            quoted_base_table_name = double_quote(base_table_name)
            quoted_partition_table_name = double_quote(self.get_partition_table(base_table_name=base_table_name))
            sql = sql.replace(quoted_base_table_name, quoted_partition_table_name)
        return sql

    def delete_related_objects(self):
        self._partition_table_op("drop")

    def truncate_related_objects(self):
        self._partition_table_op("truncate")

    def _partition_table_op(self, op):
        for base_table_name in self.RECORDS_BASE_TABLE_NAMES:
            table_name = self.get_partition_table(base_table_name=base_table_name)
            sql = f'{op} table "{table_name}";'
            try:
                run_sql(sql)
            except ProgrammingError:
                if getattr(settings, "LOG_PARTITION_WARNINGS", True):
                    logging.warning(sql)
                    log_traceback(level=logging.WARNING)
