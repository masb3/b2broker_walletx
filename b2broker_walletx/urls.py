from django.urls import include, path
from rest_framework.routers import DefaultRouter

from walletx_api.views import TransactionViewSet, WalletViewSet

router = DefaultRouter()
router.register(r"wallets", WalletViewSet)
router.register(r"transactions", TransactionViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
]
