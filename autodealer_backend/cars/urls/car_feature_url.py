from django.urls import include, path
from rest_framework.routers import DefaultRouter

from autodealer_backend.cars.viewsets import CarFeatureViewSet

router = DefaultRouter()
router.register(r"", CarFeatureViewSet, basename="car-feature")
urlpatterns = [
    path("", include(router.urls)),
]
