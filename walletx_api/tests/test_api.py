from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from walletx_api.models import Transaction, Wallet


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def wallet_1():
    return Wallet.objects.create(
        label="Test Wallet1", balance=Decimal("100.000000000000000001")
    )


@pytest.fixture
def wallet_2():
    return Wallet.objects.create(
        label="Test Wallet2", balance=Decimal("200.000000000000000001")
    )


@pytest.fixture
def wallet_3():
    return Wallet.objects.create(
        label="Test Wallet3", balance=Decimal("300.000000000000000001")
    )


@pytest.fixture
def tx_1(wallet_1):
    return Transaction.objects.create(
        wallet=wallet_1, txid="tx_1", amount=Decimal("-10.000000000000000000")
    )


@pytest.fixture
def tx_2(wallet_2):
    return Transaction.objects.create(
        wallet=wallet_2, txid="tx_2", amount=Decimal("10.000000000000000000")
    )


@pytest.fixture
def tx_3(wallet_3):
    return Transaction.objects.create(
        wallet=wallet_3, txid="tx_3", amount=Decimal("100.000000000000000000")
    )


@pytest.mark.django_db
def test_create_wallet_balance_readonly(api_client):
    url = reverse("wallet-list")
    data = {
        "data": {
            "type": "Wallet",
            "attributes": {"label": "Test Wallet", "balance": "100.000000000000000001"},
        }
    }

    response = api_client.post(url, data, format="vnd.api+json")
    assert response.status_code == status.HTTP_201_CREATED

    wallet = Wallet.objects.first()
    assert wallet.label == "Test Wallet"
    assert wallet.balance == Decimal("0.0")


@pytest.mark.django_db
def test_list_wallets(api_client, wallet_1, wallet_2, wallet_3):
    url = reverse("wallet-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 3


@pytest.mark.django_db
def test_wallet_filter_by_balance(api_client, wallet_1, wallet_2, wallet_3):
    url = reverse("wallet-list")

    # Filter by balance equals to 200
    response = api_client.get(url, {"filter[balance]": "200.000000000000000001"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["balance"] == "200.000000000000000001"

    # Filter by balance less than 300
    response = api_client.get(url, {"filter[balance__lt]": "300.000000000000000000"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2

    # Filter by balance greater than 100
    response = api_client.get(url, {"filter[balance__gt]": "100"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 3


@pytest.mark.django_db
def test_wallet_ordering(api_client, wallet_1, wallet_2, wallet_3):
    url = reverse("wallet-list")

    # Order by balance asc
    response = api_client.get(url, {"sort": "balance"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 3
    assert response.data["results"][0]["balance"] == "100.000000000000000001"
    assert response.data["results"][1]["balance"] == "200.000000000000000001"
    assert response.data["results"][2]["balance"] == "300.000000000000000001"

    # Order by balance desc
    response = api_client.get(url, {"sort": "-balance"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 3
    assert response.data["results"][2]["balance"] == "100.000000000000000001"
    assert response.data["results"][1]["balance"] == "200.000000000000000001"
    assert response.data["results"][0]["balance"] == "300.000000000000000001"


@pytest.mark.django_db
def test_wallet_search(api_client, wallet_1, wallet_2, wallet_3):
    url = reverse("wallet-list")

    response = api_client.get(url, {"filter[search]": "Wallet2"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(wallet_2.id)
    assert response.data["results"][0]["label"] == "Test Wallet2"


@pytest.mark.django_db
def test_update_wallet(api_client, wallet_1):
    url = reverse("wallet-detail", args=[wallet_1.id])
    data = {
        "data": {
            "type": "Wallet",
            "id": str(wallet_1.id),
            "attributes": {
                "label": "Django Wallet",
                "balance": "111.111111111111111111",
            },
        }
    }

    response = api_client.patch(url, data)
    assert response.status_code == status.HTTP_200_OK

    wallet_1.refresh_from_db()
    assert wallet_1.label == "Django Wallet"
    assert wallet_1.balance == Decimal("100.000000000000000001")


@pytest.mark.django_db
def test_create_transaction(api_client, wallet_1):
    url = reverse("transaction-list")
    data = {
        "data": {
            "type": "Transaction",
            "attributes": {"txid": "123", "amount": "10.0", "wallet": str(wallet_1.id)},
        }
    }

    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED

    tx = Transaction.objects.first()
    assert tx.txid == "123"
    assert tx.amount == Decimal("10.0")

    wallet_1.refresh_from_db()
    assert wallet_1.balance == Decimal("110.000000000000000001")


@pytest.mark.django_db
def test_create_transaction_unique_txid(api_client, wallet_1):
    url = reverse("transaction-list")
    data = {
        "data": {
            "type": "Transaction",
            "attributes": {"txid": "123", "amount": "10.0", "wallet": str(wallet_1.id)},
        }
    }

    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED

    tx = Transaction.objects.first()
    assert tx.txid == "123"

    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_update_transaction(api_client, wallet_1, tx_1):
    url = reverse("transaction-detail", args=[tx_1.id])
    data = {
        "data": {
            "type": "Transaction",
            "id": str(tx_1.id),
            "attributes": {
                "txid": "333",
                "amount": "111.111111111111111111",
            },
        }
    }

    response = api_client.patch(url, data)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_delete_transaction(api_client, wallet_1, tx_1):
    url = reverse("transaction-detail", args=[tx_1.id])
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_transaction_filter_by_amount(api_client, tx_1, tx_2, tx_3):
    url = reverse("transaction-list")

    # Filter by amount equals to -10
    response = api_client.get(url, {"filter[amount]": "-10.000000000000000000"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(tx_1.id)
    assert response.data["results"][0]["amount"] == "-10.000000000000000000"


@pytest.mark.django_db
def test_transaction_ordering(api_client, tx_1, tx_2, tx_3):
    url = reverse("transaction-list")

    # Order by amount asc
    response = api_client.get(url, {"sort": "amount"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 3
    assert response.data["results"][0]["id"] == str(tx_1.id)
    assert response.data["results"][0]["amount"] == "-10.000000000000000000"
    assert response.data["results"][1]["id"] == str(tx_2.id)
    assert response.data["results"][1]["amount"] == "10.000000000000000000"
    assert response.data["results"][2]["id"] == str(tx_3.id)
    assert response.data["results"][2]["amount"] == "100.000000000000000000"

    # Order by amount desc
    response = api_client.get(url, {"sort": "-amount"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 3
    assert response.data["results"][2]["id"] == str(tx_1.id)
    assert response.data["results"][2]["amount"] == "-10.000000000000000000"
    assert response.data["results"][1]["id"] == str(tx_2.id)
    assert response.data["results"][1]["amount"] == "10.000000000000000000"
    assert response.data["results"][0]["id"] == str(tx_3.id)
    assert response.data["results"][0]["amount"] == "100.000000000000000000"


@pytest.mark.django_db
def test_transaction_search(api_client, tx_1, tx_2, tx_3):
    url = reverse("transaction-list")

    # Order by amount asc
    response = api_client.get(url, {"filter[search]": "tx_2"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["id"] == str(tx_2.id)


@pytest.mark.django_db
def test_create_transaction_insufficient_wallet_balance(api_client, wallet_1):
    url = reverse("transaction-list")
    data = {
        "data": {
            "type": "Transaction",
            "attributes": {
                "txid": "123",
                "amount": "-100.000000000000000002",
                "wallet": str(wallet_1.id),
            },
        }
    }

    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
