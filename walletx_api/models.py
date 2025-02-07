import uuid
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models, transaction, IntegrityError
from django.db.models import Q, F

from walletx_api.querysets import TransactionManager


class BaseModel(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, verbose_name="ID", editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Wallet(BaseModel):
    label = models.CharField(max_length=255)
    balance = models.DecimalField(
        max_digits=30,
        decimal_places=18,
        default=Decimal("0.0"),
        validators=[
            MinValueValidator(
                Decimal("0.0"), message="Wallet balance cannot be negative."
            )
        ],
        editable=False,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(balance__gte=0), name="walletx_wallet_balance_non_negative"
            ),
        ]

    def __str__(self):
        return f"Wallet {self.id} - {self.label}"


class Transaction(BaseModel):
    wallet = models.ForeignKey(
        to="walletx_api.Wallet",
        on_delete=models.CASCADE,
        related_name="transactions",
        editable=False,
    )
    txid = models.CharField(max_length=255, unique=True, db_index=True, editable=False)
    amount = models.DecimalField(max_digits=30, decimal_places=18, editable=False)

    objects = TransactionManager()

    def __str__(self):
        return f"Transaction {self.txid} - {self.amount}"

    def save(self, *args, **kwargs):
        if self.pk and not self._state.adding:
            raise Exception("Transactions cannot be edited.")
        with transaction.atomic():
            super().save(*args, **kwargs)
            # Lock needed to avoid race conditions during balance check > 0.
            # Even there is db constraint balance >= 0, it is better to fail earlier at app level.
            updated_rows = (
                Wallet.objects.select_for_update()
                .filter(id=self.wallet.id, balance__gte=-self.amount)
                .update(balance=F("balance") + self.amount)
            )
            if updated_rows == 0:
                raise IntegrityError("Insufficient wallet balance.")
