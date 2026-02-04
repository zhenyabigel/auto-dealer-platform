from rest_framework import serializers

from autodealer_backend.cars.models import CarModel


class CarModelSerializer(serializers.ModelSerializer):
    features = serializers.SerializerMethodField()
    body_types = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=False,  # ← ДОБАВЬ ЭТО!
    )
    generation = serializers.CharField(  # ← ЯВНО УКАЖИ ПОЛЕ!
        max_length=50, required=False, allow_blank=True, default=""  # ← ДОБАВЬ DEFAULT
    )

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

    def get_features(self, obj):
        """Ленивая загрузка features через SerializerMethodField"""
        from autodealer_backend.cars.serializers.car_feature_serializer import (
            CarFeatureSerializer,
        )

        # Используем related_name="features" из модели CarFeature
        features = obj.features.all()
        return CarFeatureSerializer(features, many=True).data

    def validate_production_start(self, value):
        if value < 1900 or value > 2100:
            raise serializers.ValidationError("Год должен быть между 1900 и 2100")
        return value

    def validate_production_end(self, value):
        if value is not None and (value < 1900 or value > 2100):
            raise serializers.ValidationError("Год должен быть между 1900 и 2100")
        return value

    def validate(self, data):
        start = data.get("production_start")
        end = data.get("production_end")

        if end is not None and start is not None and end < start:
            raise serializers.ValidationError(
                "Год окончания не может быть раньше начала"
            )

        # Проверяем body_types
        body_types = data.get("body_types", [])
        if not body_types:
            raise serializers.ValidationError(
                {"body_types": "Поле body_types не может быть пустым"}
            )

        return data

    def create(self, validated_data):
        body_types = validated_data.pop("body_types", [])
        car_model = CarModel.objects.create(**validated_data, body_types=body_types)
        return car_model

    def update(self, instance, validated_data):
        body_types = validated_data.pop("body_types", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if body_types is not None:
            instance.body_types = body_types

        instance.save()
        return instance
