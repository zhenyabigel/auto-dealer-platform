from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from .filters import DealFilter, OfferFilter
from .models import Deal, Offer
from .serializers import DealSerializer, OfferSerializer


class OfferViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = Offer.objects.select_related("customer").all()
    serializer_class = OfferSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = OfferFilter
    search_fields = ["car_model", "customer__user__email"]
    ordering_fields = ["max_price", "created_at"]

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), permissions.IsAuthenticatedOrReadOnly()]
        return [IsAuthenticated()]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "car_model",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Фильтр по модели авто (регистронезависимый)",
            ),
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                enum=["pending", "accepted", "rejected"],
                description="Статус предложения",
            ),
            openapi.Parameter(
                "max_price__gt",
                openapi.IN_QUERY,
                type=openapi.TYPE_NUMBER,
                description="Минимальная максимальная цена",
            ),
            openapi.Parameter(
                "created_at_after",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format="date",
                description="Дата создания после (YYYY-MM-DD)",
            ),
            openapi.Parameter(
                "ordering",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Сортировка: max_price, -max_price, created_at, -created_at",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class DealViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    queryset = Deal.objects.select_related("customer", "dealer", "car").all()
    serializer_class = DealSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = DealFilter
    search_fields = ["car__brand", "car__model", "dealer__name"]
    ordering_fields = ["price", "date"]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "dealer__name",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Фильтр по названию дилера",
            ),
            openapi.Parameter(
                "price__gt",
                openapi.IN_QUERY,
                type=openapi.TYPE_NUMBER,
                description="Минимальная цена сделки",
            ),
            openapi.Parameter(
                "date_after",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format="date",
                description="Дата сделки после (YYYY-MM-DD)",
            ),
            openapi.Parameter(
                "ordering",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Сортировка: price, -price, date, -date",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
