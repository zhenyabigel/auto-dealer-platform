from django.urls import include, path
from rest_framework.routers import DefaultRouter

from autodealer_backend.users.viewsets.user_viewset import UserViewSet

router = DefaultRouter()
router.register(r"", UserViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
]
