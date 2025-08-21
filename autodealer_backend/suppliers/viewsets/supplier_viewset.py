from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, mixins, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from autodealer_backend.suppliers.filters import SupplierFilter
from autodealer_backend.suppliers.models import Supplier
from autodealer_backend.suppliers.serializers import SupplierSerializer


class SupplierViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    queryset = Supplier.objects.select_related("user", "country").prefetch_related(
        "offers"
    )
    serializer_class = SupplierSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = SupplierFilter
    search_fields = [
        "name",
        "legal_name",
        "country__name",
        "city",
        "contact_person",
        "email",
    ]
    ordering_fields = [
        "name",
        "year_established",
        "discount_for_dealers",
        "average_delivery_time",
        "created_at",
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
                description="Название поставщика (поиск по подстроке)",
            ),
            openapi.Parameter(
                "has_active_offers",
                openapi.IN_QUERY,
                type=openapi.TYPE_BOOLEAN,
                description="Только с активными предложениями",
            ),
            openapi.Parameter(
                "supplier_type",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                enum=[x[0] for x in Supplier.SUPPLIER_TYPES],
                description="Тип поставщика",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
