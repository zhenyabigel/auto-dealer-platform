from rest_framework import serializers

from autodealer_backend.cars.models.car_model import CarModel
from autodealer_backend.cars.serializers import CarModelSerializer
from autodealer_backend.dealers.models import DealerStock
from autodealer_backend.suppliers.models import Supplier
from autodealer_backend.suppliers.serializers import SupplierSerializer


class DealerStockSerializer(serializers.ModelSerializer):
    dealer = serializers.SlugRelatedField(slug_field="name", read_only=True)
    car_model = CarModelSerializer(read_only=True)
    car_model_id = serializers.PrimaryKeyRelatedField(
        queryset=CarModel.objects.all(), source="car_model", write_only=True
    )
    supplier = SupplierSerializer(read_only=True)
    supplier_id = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(),
        source="supplier",
        write_only=True,
        allow_null=True,
    )
    condition_display = serializers.CharField(
        source="get_condition_display", read_only=True
    )
    profit = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    days_in_stock = serializers.IntegerField(read_only=True)

    class Meta:
        model = DealerStock
        fields = [
            "id",
            "dealer",
            "car_model",
            "car_model_id",
            "supplier",
            "supplier_id",
            "purchase_price",
            "selling_price",
            "vin",
            "mileage",
            "color",
            "condition",
            "condition_display",
            "is_sold",
            "arrival_date",
            "is_active",
            "profit",
            "days_in_stock",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "profit", "days_in_stock"]
        extra_kwargs = {
            "purchase_price": {"min_value": 0},
            "selling_price": {"min_value": 0},
            "mileage": {"min_value": 0},
        }

    def validate_vin(self, value):
        if value and len(value) != 17:
            raise serializers.ValidationError("VIN должен содержать 17 символов")
        return value

    def validate(self, data):
        if data.get("selling_price", 0) < data.get("purchase_price", 0):
            raise serializers.ValidationError(
                "Цена продажи не может быть меньше цены покупки"
            )
        return data
