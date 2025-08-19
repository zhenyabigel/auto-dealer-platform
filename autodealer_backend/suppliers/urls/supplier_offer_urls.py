from django.urls import include, path
from rest_framework.routers import DefaultRouter

from autodealer_backend.suppliers.viewsets import SupplierOfferViewSet

router = DefaultRouter()
router.register(r"supplier-offer", SupplierOfferViewSet, basename="supplier-offer")
urlpatterns = [
    path("", include(router.urls)),
]
