from django.urls import include, path
from rest_framework.routers import DefaultRouter

from autodealer_backend.deals.viewsets import OfferViewSet

router = DefaultRouter()
router.register(r"", OfferViewSet, basename="offers")
urlpatterns = [
    path("", include(router.urls)),
]
