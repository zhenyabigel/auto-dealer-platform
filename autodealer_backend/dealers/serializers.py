from decimal import Decimal

from django.core.validators import MinValueValidator
from rest_framework import serializers

from .models import Dealer


class DealerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dealer
        fields = "__all__"
        extra_kwargs = {"balance": {"validators": [MinValueValidator(Decimal("0.00"))]}}

    def validate_balance(self, value):
        if value < 0:
            raise serializers.ValidationError("Balance cannot be negative")
        return value

    def validate_preferred_car_brands(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Must be a list")
        return value

    def validate_preferred_car_characteristics(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Must be a dictionary")
        return value
