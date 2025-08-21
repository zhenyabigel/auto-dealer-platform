from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, mixins, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from autodealer_backend.suppliers.filters.supplier_offer_filter import (
    SupplierOfferFilter,
)
from autodealer_backend.suppliers.models import SupplierOffer
from autodealer_backend.suppliers.serializers import SupplierOfferSerializer


class SupplierOfferViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    queryset = SupplierOffer.objects.select_related("supplier", "car_model").filter(
        is_active=True
    )
    serializer_class = SupplierOfferSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = SupplierOfferFilter
    search_fields = ["raw_brand", "raw_model", "supplier__username"]
    ordering_fields = ["price", "valid_from", "valid_to", "discount_percent"]
    ordering = ["price"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return [IsAuthenticated(), permissions.DjangoModelPermissions()]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "valid_now",
                openapi.IN_QUERY,
                type=openapi.TYPE_BOOLEAN,
                description="Только действующие предложения",
            ),
            openapi.Parameter(
                "price__lt",
                openapi.IN_QUERY,
                type=openapi.TYPE_NUMBER,
                description="Цена до",
            ),
            openapi.Parameter(
                "car_model__brand",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Бренд автомобиля",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
