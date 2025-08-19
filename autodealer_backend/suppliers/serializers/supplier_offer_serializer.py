from rest_framework import serializers

from autodealer_backend.cars.models import CarModel
from autodealer_backend.suppliers.models import SupplierOffer
from autodealer_backend.users.models import User


class SupplierOfferSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    car_model_info = serializers.CharField(source="car_model.__str__", read_only=True)
    car_name = serializers.CharField(read_only=True)
    is_active_now = serializers.BooleanField(read_only=True)

    supplier_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="supplier"),
        source="supplier",
        write_only=True,
    )
    car_model_id = serializers.PrimaryKeyRelatedField(
        queryset=CarModel.objects.all(),
        source="car_model",
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = SupplierOffer
        fields = [
            "id",
            "supplier",
            "supplier_id",
            "supplier_name",
            "car_model",
            "car_model_id",
            "car_model_info",
            "raw_brand",
            "raw_model",
            "raw_specs",
            "price",
            "quantity_available",
            "discount_percent",
            "valid_from",
            "valid_to",
            "delivery_days",
            "is_new",
            "warranty_months",
            "is_active",
            "car_name",
            "is_active_now",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate(self, data):
        if not data.get("car_model") and not (
            data.get("raw_brand") and data.get("raw_model")
        ):
            raise serializers.ValidationError(
                "Необходимо указать либо car_model, либо raw_brand и raw_model"
            )
        return data
