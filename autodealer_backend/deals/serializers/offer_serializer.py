from rest_framework import serializers

from autodealer_backend.cars.models import CarModel
from autodealer_backend.deals.models.offer_model import Offer


class OfferSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.username", read_only=True)
    car_model_info = serializers.CharField(source="car_model.__str__", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    is_expired = serializers.BooleanField(read_only=True)

    car_model_id = serializers.PrimaryKeyRelatedField(
        queryset=CarModel.objects.all(), source="car_model", write_only=True
    )

    class Meta:
        model = Offer
        fields = [
            "id",
            "customer",
            "customer_name",
            "car_model_id",
            "car_model_info",
            "max_price",
            "status",
            "status_display",
            "expiry_date",
            "is_expired",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "car_model",
            "customer",
            "status",
            "created_at",
            "updated_at",
        ]

    def validate_max_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Цена должна быть положительной")
        return value
