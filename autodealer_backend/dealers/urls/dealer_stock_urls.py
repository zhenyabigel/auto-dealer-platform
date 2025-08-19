from django.urls import include, path
from rest_framework.routers import DefaultRouter

from autodealer_backend.dealers.viewsets import DealerStockViewSet

router = DefaultRouter()
router.register(r"", DealerStockViewSet, basename="dealer-stock")

urlpatterns = [
    path("", include(router.urls)),
]
