from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from .filters import CarFilter, PromotionFilter, SupplierFilter
from .models import Car, Promotion, Supplier
from .serializers import CarSerializer, PromotionSerializer, SupplierSerializer


class CarViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = CarFilter
    search_fields = ["brand", "model"]
    ordering_fields = ["price", "year", "created_at"]
    ordering = ["-created_at"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        elif self.action in ["create", "update", "partial_update"]:
            return [IsAuthenticated(), permissions.DjangoModelPermissions()]
        return super().get_permissions()

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "brand",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Фильтр по бренду",
            ),
            openapi.Parameter(
                "model",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Фильтр по модели",
            ),
            openapi.Parameter(
                "year__gt",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="Год выпуска от",
            ),
            openapi.Parameter(
                "price__lt",
                openapi.IN_QUERY,
                type=openapi.TYPE_NUMBER,
                description="Цена до",
            ),
            openapi.Parameter(
                "engine_type",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                enum=["petrol", "diesel", "electric", "hybrid"],
                description="Тип двигателя",
            ),
            openapi.Parameter(
                "dealer_name",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Название дилера",
            ),
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Поиск по тексту",
            ),
            openapi.Parameter(
                "ordering",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Сортировка (price, -year и т.д.)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class SupplierViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = SupplierFilter
    search_fields = ["name"]
    ordering_fields = ["year_established", "discount_for_dealers", "created_at"]
    ordering = ["name"]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "name",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Название поставщика",
            ),
            openapi.Parameter(
                "year_established__gt",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="Год основания от",
            ),
            openapi.Parameter(
                "discount_for_dealers",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="Скидка для дилеров",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class PromotionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = PromotionFilter
    search_fields = ["name", "description"]
    ordering_fields = ["start_date", "end_date", "discount_percent"]
    ordering = ["-start_date"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return [IsAuthenticated(), permissions.DjangoModelPermissions()]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "name",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Название акции",
            ),
            openapi.Parameter(
                "active",
                openapi.IN_QUERY,
                type=openapi.TYPE_BOOLEAN,
                description="Только активные акции",
            ),
            openapi.Parameter(
                "discount_percent__gt",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="Скидка от",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
