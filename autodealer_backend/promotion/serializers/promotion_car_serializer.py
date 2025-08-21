from rest_framework import serializers

from autodealer_backend.cars.models import CarModel
from autodealer_backend.cars.serializers import CarModelSerializer
from autodealer_backend.promotion.models.promotion_car_model import PromotionCar
from autodealer_backend.promotion.models.promotion_model import Promotion


class PromotionCarSerializer(serializers.ModelSerializer):
    car_model_info = CarModelSerializer(read_only=True)
    car_model_name = serializers.CharField(source="car_model.__str__", read_only=True)
    promotion_name = serializers.CharField(source="promotion.name", read_only=True)
    is_promotion_active = serializers.BooleanField(
        source="promotion.is_active_now", read_only=True
    )

    car_model_id = serializers.PrimaryKeyRelatedField(
        queryset=CarModel.objects.all(), source="car_model", write_only=True
    )
    promotion_id = serializers.PrimaryKeyRelatedField(
        queryset=Promotion.objects.all(), source="promotion", write_only=True
    )

    class Meta:
        model = PromotionCar
        fields = [
            "id",
            "promotion",
            "promotion_id",
            "promotion_name",
            "car_model",
            "car_model_id",
            "car_model_info",
            "car_model_name",
            "special_price",
            "is_promotion_active",
        ]
        read_only_fields = ["promotion_name", "car_model_name", "is_promotion_active"]
