from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, mixins, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from autodealer_backend.promotion.filters import PromotionFilter
from autodealer_backend.promotion.models.promotion_model import Promotion
from autodealer_backend.promotion.serializers import PromotionSerializer


class PromotionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = Promotion.objects.select_related("dealer").prefetch_related(
        "promotion_cars__car_model"
    )
    serializer_class = PromotionSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = PromotionFilter
    search_fields = ["name", "description"]
    ordering_fields = ["start_date", "end_date", "discount_percent", "created_at"]
    ordering = ["-start_date"]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.query_params.get("active_only"):
            queryset = queryset.filter(is_active=True)
        return queryset

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return [IsAuthenticated(), permissions.DjangoModelPermissions()]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "active_now",
                openapi.IN_QUERY,
                type=openapi.TYPE_BOOLEAN,
                description="Только активные сейчас акции",
            ),
            openapi.Parameter(
                "car_brand",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Бренд автомобиля",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
