from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets

from autodealer_backend.promotion.filters import PromotionCarFilter
from autodealer_backend.promotion.models.promotion_car_model import PromotionCar
from autodealer_backend.promotion.serializers import PromotionCarSerializer


class PromotionCarViewSet(viewsets.ModelViewSet):
    queryset = PromotionCar.objects.select_related(
        "promotion", "car_model"
    ).prefetch_related("car_model__features")
    serializer_class = PromotionCarSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PromotionCarFilter
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()

        promotion_id = self.request.query_params.get("promotion")
        if promotion_id:
            qs = qs.filter(promotion_id=promotion_id)

        return qs
