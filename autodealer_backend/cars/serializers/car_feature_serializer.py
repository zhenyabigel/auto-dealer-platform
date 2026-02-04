from rest_framework import serializers

from autodealer_backend.cars.models import CarFeature, CarModel


class CarFeatureSerializer(serializers.ModelSerializer):
    car_model = serializers.PrimaryKeyRelatedField(queryset=CarModel.objects.all())

    class Meta:
        model = CarFeature
        fields = [
            "id",
            "car_model",
            "category",
            "name",
            "description",
            "is_standard",
            "is_optional",
        ]

    def validate(self, data):
        if "is_standard" in data and "is_optional" not in data:
            data["is_optional"] = not data["is_standard"]
        return data

    def create(self, validated_data):
        if "is_standard" in validated_data and "is_optional" not in validated_data:
            validated_data["is_optional"] = not validated_data["is_standard"]
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "is_standard" in validated_data and "is_optional" not in validated_data:
            validated_data["is_optional"] = not validated_data["is_standard"]
        return super().update(instance, validated_data)
