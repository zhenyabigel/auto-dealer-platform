from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, mixins, permissions, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from autodealer_backend.dealers.filters import DealerFilter
from autodealer_backend.dealers.models import Dealer
from autodealer_backend.dealers.permissions import IsAdminOrDealerOwner
from autodealer_backend.dealers.serializers import DealerSerializer

User = get_user_model()


class DealerViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    queryset = (
        Dealer.objects.select_related("user")
        .prefetch_related("dealer_stock", "preferred_car_models")
        .all()
    )
    serializer_class = DealerSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = DealerFilter
    search_fields = ["name", "legal_name", "contact_person", "email"]
    ordering_fields = [
        "name",
        "balance",
        "created_at",
        "stock_count",
        "total_stock_value",
    ]
    ordering = ["name"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        elif self.action in ["update", "partial_update"]:
            return [IsAuthenticated(), IsAdminOrDealerOwner()]
        return [IsAuthenticated(), permissions.DjangoModelPermissions()]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "name",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Название дилера (поиск по подстроке)",
            ),
            openapi.Parameter(
                "has_stock",
                openapi.IN_QUERY,
                type=openapi.TYPE_BOOLEAN,
                description="Только с автомобилями в наличии",
            ),
            openapi.Parameter(
                "dealer_type",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                enum=[x[0] for x in Dealer.DEALER_TYPES],
                description="Тип дилера",
            ),
            openapi.Parameter(
                "ordering",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Сортировка: name, -name, balance, -balance и т.д.",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        # Получаем ID пользователя из исходных данных запроса
        user_id = self.request.data.get("user")

        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {"user": "Пользователь с указанным ID не существует."}
                )

            # Только админ может создать профиль за другого
            if user != self.request.user and not self.request.user.is_staff:
                self.permission_denied(
                    self.request, "Вы можете создавать профиль только для себя"
                )
            if user.role != "dealer":
                raise serializers.ValidationError(
                    {"user": "Пользователь должен быть с ролью 'dealer'"}
                )
        else:
            # Автоматически использовать request.user
            user = self.request.user
            if user.role != "dealer":
                raise serializers.ValidationError(
                    {"user": "Только дилеры могут иметь профиль"}
                )

        # Передаем пользователя напрямую в save, обходя сериализатор
        serializer.save(user=user)
