from django.urls import include, path
from rest_framework.routers import DefaultRouter

from autodealer_backend.dealers.viewsets import DealerViewSet

router = DefaultRouter()
router.register(r"", DealerViewSet, basename="dealers")

urlpatterns = [
    path("", include(router.urls)),
]
