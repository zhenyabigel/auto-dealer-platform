from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, mixins, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import GenericViewSet

from autodealer_backend.dealers.filters import DealerStockFilter
from autodealer_backend.dealers.models import Dealer, DealerStock
from autodealer_backend.dealers.permissions.dealer_stock_admin_permissions import (
    IsAdminOrDealerStockOwner,
)
from autodealer_backend.dealers.serializers import DealerStockSerializer


class DealerStockViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
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
    permission_classes = [permissions.IsAuthenticated]  # Default permission

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.IsAuthenticated()]
        elif self.action in ["create", "update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated(), IsAdminOrDealerStockOwner()]
        return super().get_permissions()

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

    def perform_create(self, serializer):
        dealer_id = self.request.data.get("dealer")
        if dealer_id:
            try:
                dealer = Dealer.objects.get(id=dealer_id)
            except Dealer.DoesNotExist:
                raise PermissionDenied("Указанный дилер не существует.")

            if not self.request.user.is_staff and dealer.user != self.request.user:
                self.permission_denied(
                    self.request,
                    "Вы можете добавлять автомобили только в свой автосалон.",
                )
        else:
            try:
                dealer = self.request.user.dealer_profile
            except Dealer.DoesNotExist:
                self.permission_denied(
                    self.request,
                    "Только дилеры и администраторы могут добавлять автомобили на склад.",
                )

        serializer.save(dealer=dealer)
