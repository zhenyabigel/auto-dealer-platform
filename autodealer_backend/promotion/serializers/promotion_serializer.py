from rest_framework import serializers

from autodealer_backend.promotion.models.promotion_model import Promotion
from autodealer_backend.promotion.serializers import PromotionCarSerializer


class PromotionSerializer(serializers.ModelSerializer):
    dealer_name = serializers.CharField(source="dealer.name", read_only=True)
    promotion_cars = PromotionCarSerializer(many=True, read_only=True)
    is_active_now = serializers.BooleanField(read_only=True)
    promotion_type_display = serializers.CharField(
        source="get_promotion_type_display", read_only=True
    )

    class Meta:
        model = Promotion
        fields = [
            "id",
            "name",
            "description",
            "promotion_type",
            "promotion_type_display",
            "start_date",
            "end_date",
            "discount_percent",
            "max_discount_amount",
            "dealer",
            "dealer_name",
            "promotion_cars",
            "is_active",
            "is_active_now",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "is_active_now", "dealer_name"]

    def validate(self, data):
        if data.get("promotion_type") == "dealer" and not data.get("dealer"):
            raise serializers.ValidationError(
                "Для акций дилера должен быть указан дилер"
            )
        if data.get("start_date") and data.get("end_date"):
            if data["start_date"] >= data["end_date"]:
                raise serializers.ValidationError(
                    "Дата начала должна быть раньше даты окончания"
                )
        return data
