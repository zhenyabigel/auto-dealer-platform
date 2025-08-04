from decimal import Decimal

from django.core.validators import MinValueValidator
from rest_framework import serializers

from .models import Dealer


class DealerSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()
    is_active = serializers.BooleanField(default=True)

    class Meta:
        model = Dealer
        fields = [
            "id",
            "name",
            "location",
            "balance",
            "preferred_car_brands",
            "preferred_car_characteristics",
            "is_active",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "name": {"min_length": 2, "max_length": 100},
            "balance": {
                "validators": [MinValueValidator(Decimal("0.00"))],
                "max_digits": 12,
                "decimal_places": 2,
            },
            "preferred_car_brands": {"required": False},
            "preferred_car_characteristics": {"required": False},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }

    def get_location(self, obj):
        return {"code": obj.location.code, "name": obj.location.name}

    def validate_preferred_car_brands(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Preferred car brands must be a list")
        return value

    def validate_preferred_car_characteristics(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Preferred car characteristics must be a dictionary"
            )
        return value
