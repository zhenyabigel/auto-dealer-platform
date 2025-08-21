from rest_framework import serializers

from autodealer_backend.cars.models import CarFeature


class CarFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarFeature
        fields = ["id", "category", "name", "description", "is_standard", "is_optional"]
