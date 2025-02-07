from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import MethodNotAllowed, ValidationError
from rest_framework.validators import UniqueValidator

from walletx_api.models import Transaction, Wallet


class TransactionSerializer(serializers.ModelSerializer):
    txid = serializers.CharField(
        max_length=255,
        validators=[UniqueValidator(queryset=Transaction.objects.all())],
    )
    amount = serializers.DecimalField(max_digits=30, decimal_places=18)
    wallet = serializers.PrimaryKeyRelatedField(queryset=Wallet.objects.all())

    class Meta:
        model = Transaction
        fields = ["id", "wallet", "txid", "amount"]

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError as e:
            raise ValidationError({"detail": str(e)})

    def update(self, instance, validated_data):
        raise MethodNotAllowed("Transactions are not editable.")


class WalletSerializer(serializers.ModelSerializer):
    transactions = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Wallet
        fields = ["id", "label", "balance", "transactions"]
        read_only_fields = ["balance"]
