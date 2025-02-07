from rest_framework import mixins, viewsets

from walletx_api.models import Transaction, Wallet
from walletx_api.serializers import TransactionSerializer, WalletSerializer


class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    ordering_fields = ["balance", "created_at", "updated_at"]
    search_fields = ["balance", "label"]
    filterset_fields = {
        "id": ("exact", "in"),
        "label": ("icontains", "iexact", "contains"),
        "balance": ("exact", "lt", "gt", "gte", "lte", "in"),
    }


class TransactionViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    ordering_fields = ["amount", "created_at"]
    search_fields = ["amount", "txid"]
    filterset_fields = {
        "id": ("exact", "in"),
        "txid": ("icontains", "iexact", "contains"),
        "amount": ("exact", "lt", "gt", "gte", "lte", "in"),
    }
