from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, mixins, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from autodealer_backend.cars.filters import CarModelFilter
from autodealer_backend.cars.models import CarModel
from autodealer_backend.cars.serializers import CarModelSerializer


class CarModelViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    queryset = CarModel.objects.prefetch_related("features").all()
    serializer_class = CarModelSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = CarModelFilter
    search_fields = ["brand", "model", "generation"]
    ordering_fields = ["brand", "model", "production_start", "power", "engine_volume"]
    ordering = ["brand", "model"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return [IsAuthenticated(), permissions.DjangoModelPermissions()]

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
                "production_start__gt",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="Год выпуска от",
            ),
            openapi.Parameter(
                "engine_type",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                enum=["petrol", "diesel", "electric", "hybrid"],
                description="Тип двигателя",
            ),
            openapi.Parameter(
                "power__gt",
                openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="Мощность от (л.с.)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
