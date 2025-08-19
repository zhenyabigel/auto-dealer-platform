from rest_framework import serializers

from autodealer_backend.cars.models import CarModel
from autodealer_backend.cars.serializers import CarFeatureSerializer


class CarModelSerializer(serializers.ModelSerializer):
    features = CarFeatureSerializer(many=True, read_only=True)
    body_types = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = CarModel
        fields = [
            "id",
            "brand",
            "model",
            "generation",
            "production_start",
            "production_end",
            "engine_type",
            "engine_volume",
            "power",
            "transmission",
            "drive_type",
            "fuel_consumption",
            "length",
            "width",
            "height",
            "weight",
            "body_types",
            "seats",
            "doors",
            "features",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
