from django.urls import path, include
from rest_framework.routers import DefaultRouter

from walletx_api.views import WalletViewSet, TransactionViewSet

router = DefaultRouter()
router.register(r"wallets", WalletViewSet)
router.register(r"transactions", TransactionViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
]
