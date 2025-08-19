from django.urls import include, path
from rest_framework.routers import DefaultRouter

from autodealer_backend.deals.viewsets import DealViewSet

router = DefaultRouter()
router.register(r"", DealViewSet, basename="deals")
urlpatterns = [
    path("", include(router.urls)),
]
