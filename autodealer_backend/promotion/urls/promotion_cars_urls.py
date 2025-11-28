from django.urls import include, path
from rest_framework.routers import DefaultRouter

from autodealer_backend.promotion.viewsets import PromotionCarViewSet

router = DefaultRouter()
router.register(r"", PromotionCarViewSet, basename="promotion-car")
urlpatterns = [
    path("", include(router.urls)),
]
