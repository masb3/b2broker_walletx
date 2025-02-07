from django.db import models


class TransactionQuerySet(models.QuerySet):
    def update(self, *args, **kwargs):
        raise Exception("Transactions cannot be edited.")


class TransactionManager(models.Manager):
    def get_queryset(self):
        return TransactionQuerySet(self.model, using=self._db)
