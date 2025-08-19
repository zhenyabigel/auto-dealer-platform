from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from autodealer_backend.users.filters import UserFilter
from autodealer_backend.users.models import User
from autodealer_backend.users.serializers import (
    UserProfileUpdateSerializer,
    UserSerializer,
)


class UserViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "update":
            return UserProfileUpdateSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == "list":
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    @swagger_auto_schema(
        operation_description="Получить информацию о текущем пользователе",
        responses={200: UserSerializer, 401: "Не авторизован"},
    )
    @action(detail=False, methods=["get"])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Получить список пользователей (только для администраторов)",
        manual_parameters=[
            openapi.Parameter(
                "role",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                enum=[role[0] for role in User.ROLE_CHOICES],
                description="Фильтр по роли пользователя",
            ),
            openapi.Parameter(
                "is_verified",
                openapi.IN_QUERY,
                type=openapi.TYPE_BOOLEAN,
                description="Фильтр по статусу верификации",
            ),
        ],
        responses={200: UserSerializer(many=True), 403: "Доступ запрещен"},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Обновить профиль пользователя",
        request_body=UserProfileUpdateSerializer,
        responses={200: UserSerializer, 400: "Неверные данные", 401: "Не авторизован"},
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Частичное обновление профиля пользователя",
        request_body=UserProfileUpdateSerializer,
        responses={200: UserSerializer, 400: "Неверные данные", 401: "Не авторизован"},
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Получить информацию о пользователе по ID",
        responses={
            200: UserSerializer,
            404: "Пользователь не найден",
            401: "Не авторизован",
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
