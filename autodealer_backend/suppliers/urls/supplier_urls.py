from django.urls import include, path
from rest_framework.routers import DefaultRouter

from autodealer_backend.suppliers.viewsets import SupplierViewSet

router = DefaultRouter()
router.register(r"", SupplierViewSet, basename="suppliers")
urlpatterns = [
    path("", include(router.urls)),
]
