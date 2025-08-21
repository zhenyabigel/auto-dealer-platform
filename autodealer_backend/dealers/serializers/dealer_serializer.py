from decimal import Decimal

from django.core.validators import MinValueValidator
from rest_framework import serializers

from autodealer_backend.cars.serializers import CarModelSerializer
from autodealer_backend.dealers.models import Dealer


class DealerSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    location = serializers.SerializerMethodField()
    stock_count = serializers.IntegerField(read_only=True)
    total_stock_value = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    dealer_type_display = serializers.CharField(
        source="get_dealer_type_display", read_only=True
    )
    preferred_car_models = CarModelSerializer(many=True, read_only=True)

    class Meta:
        model = Dealer
        fields = [
            "id",
            "user",
            "name",
            "legal_name",
            "dealer_type",
            "dealer_type_display",
            "location",
            "address",
            "phone",
            "email",
            "website",
            "contact_person",
            "balance",
            "stock_count",
            "total_stock_value",
            "is_active",
            "created_at",
            "updated_at",
            "preferred_car_models",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
            "stock_count",
            "total_stock_value",
        ]
        extra_kwargs = {"balance": {"validators": [MinValueValidator(Decimal("0.00"))]}}

    def get_location(self, obj):
        return obj.location.name if obj.location else None

    def validate_balance(self, value):
        if value < 0:
            raise serializers.ValidationError("Баланс не может быть отрицательным")
        return value
