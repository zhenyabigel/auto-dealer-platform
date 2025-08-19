from django.urls import include, path
from rest_framework.routers import DefaultRouter

from autodealer_backend.users.viewsets.auth_viewset import AuthViewSet

router = DefaultRouter()
router.register(r"", AuthViewSet, basename="auth")

urlpatterns = [
    path("", include(router.urls)),
]
