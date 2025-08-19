from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, mixins, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from autodealer_backend.dealers.filters import DealerFilter
from autodealer_backend.dealers.models import Dealer
from autodealer_backend.dealers.serializers import DealerSerializer


class DealerViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    queryset = (
        Dealer.objects.select_related("user", "location")
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
    search_fields = ["name", "legal_name", "location__name", "contact_person", "email"]
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
