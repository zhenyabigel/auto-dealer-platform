from django.urls import include, path
from rest_framework.routers import DefaultRouter

from autodealer_backend.cars.viewsets import CarModelViewSet

router = DefaultRouter()
router.register(r"", CarModelViewSet, basename="car-models")
urlpatterns = [
    path("", include(router.urls)),
]
