from decimal import Decimal

import pytest
from django.db import IntegrityError

from walletx_api.models import Transaction, Wallet


@pytest.fixture
def wallet():
    return Wallet.objects.create(
        label="Test Wallet", balance=Decimal("100.000000000000000001")
    )


@pytest.mark.django_db
def test_wallet_creation(wallet):
    assert wallet.id is not None
    assert wallet.label == "Test Wallet"
    assert wallet.balance == Decimal("100.000000000000000001")


@pytest.mark.django_db
def test_wallet_balance_non_negative():
    with pytest.raises(IntegrityError):
        Wallet.objects.create(
            label="Test Wallet", balance=Decimal("-0.000000000000000001")
        )


@pytest.mark.django_db
def test_transaction_creation(wallet):
    tx = Transaction.objects.create(
        wallet=wallet, txid="tx123", amount=Decimal("-10.000000000000000000")
    )

    assert tx.id is not None
    assert tx.wallet == wallet
    assert tx.txid == "tx123"
    assert tx.amount == Decimal("-10.000000000000000000")

    wallet.refresh_from_db()
    assert wallet.balance == Decimal("90.000000000000000001")


@pytest.mark.django_db
def test_transaction_update(wallet):
    tx = Transaction.objects.create(
        wallet=wallet, txid="tx123", amount=Decimal("-10.000000000000000000")
    )

    with pytest.raises(Exception):
        tx.amount = Decimal("10.000000000000000000")
        tx.save()


@pytest.mark.django_db
def test_transaction_update_with_update_queryset(wallet):
    tx = Transaction.objects.create(
        wallet=wallet, txid="tx123", amount=Decimal("-10.000000000000000000")
    )

    wallet.refresh_from_db()
    assert wallet.balance == Decimal("90.000000000000000001")

    with pytest.raises(Exception):
        Transaction.objects.filter(id=tx.id).update(
            amount=Decimal("10.000000000000000000")
        )

    tx.refresh_from_db()
    assert tx.amount == Decimal("-10.000000000000000000")

    wallet.refresh_from_db()
    assert wallet.balance == Decimal("90.000000000000000001")


@pytest.mark.django_db
def test_insufficient_wallet_balance(wallet):
    with pytest.raises(IntegrityError):
        Transaction.objects.create(
            wallet=wallet, txid="tx123", amount=Decimal("-100.000000000000000002")
        )

    wallet.refresh_from_db()
    assert wallet.balance == Decimal("100.000000000000000001")
