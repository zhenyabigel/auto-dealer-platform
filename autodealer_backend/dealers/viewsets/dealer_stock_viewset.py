from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, mixins, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from autodealer_backend.dealers.filters import DealerStockFilter
from autodealer_backend.dealers.models import DealerStock
from autodealer_backend.dealers.serializers import DealerStockSerializer


class DealerStockViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    queryset = DealerStock.objects.select_related(
        "dealer", "car_model", "supplier"
    ).all()
    serializer_class = DealerStockSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = DealerStockFilter
    search_fields = ["car_model__brand", "car_model__model", "vin", "dealer__name"]
    ordering_fields = ["selling_price", "arrival_date", "mileage"]
    ordering = ["-arrival_date"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return [IsAuthenticated(), permissions.DjangoModelPermissions()]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "dealer",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Название дилера",
            ),
            openapi.Parameter(
                "car_brand",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Бренд автомобиля",
            ),
            openapi.Parameter(
                "is_available",
                openapi.IN_QUERY,
                type=openapi.TYPE_BOOLEAN,
                description="Только доступные автомобили",
            ),
            openapi.Parameter(
                "price__gt",
                openapi.IN_QUERY,
                type=openapi.TYPE_NUMBER,
                description="Цена от",
            ),
            openapi.Parameter(
                "price__lt",
                openapi.IN_QUERY,
                type=openapi.TYPE_NUMBER,
                description="Цена до",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
