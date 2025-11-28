from django.urls import include, path
from rest_framework.routers import DefaultRouter

from autodealer_backend.promotion.viewsets import PromotionViewSet

router = DefaultRouter()
router.register(r"", PromotionViewSet, basename="promotion")
urlpatterns = [
    path("", include(router.urls)),
]
