import pytest

from autodealer_backend.promotion.serializers import PromotionCarSerializer
from autodealer_backend.promotion.tests.factories.promotion_car_factory import (
    PromotionCarFactory,
)


@pytest.mark.django_db
class TestPromotionCarSerializer:

    def test_serializer_with_valid_data(self):
        promotion_car = PromotionCarFactory()
        serializer = PromotionCarSerializer(promotion_car)

        data = serializer.data
        assert data["id"] == promotion_car.id
        assert "promotion_name" in data
        assert "car_model_name" in data
        assert "car_model_info" in data
        assert "is_promotion_active" in data

    def test_serializer_validation_valid(self):
        promotion_car = PromotionCarFactory()
        data = {
            "promotion_id": promotion_car.promotion.id,
            "car_model_id": promotion_car.car_model.id,
            "special_price": 1500000.00,
        }

        serializer = PromotionCarSerializer(data=data)
        assert serializer.is_valid()

    def test_write_only_fields(self):
        promotion_car = PromotionCarFactory()
        data = {
            "promotion_id": promotion_car.promotion.id,
            "car_model_id": promotion_car.car_model.id,
            "special_price": 1600000.00,
        }

        serializer = PromotionCarSerializer(data=data)
        assert serializer.is_valid()

        instance = serializer.save()
        assert instance.promotion.id == promotion_car.promotion.id
        assert instance.car_model.id == promotion_car.car_model.id
        assert instance.special_price == 1600000.00

    def test_read_only_fields(self):
        promotion_car = PromotionCarFactory()
        data = {
            "promotion_id": promotion_car.promotion.id,
            "car_model_id": promotion_car.car_model.id,
            "promotion_name": "Новое название",
            "special_price": 1500000.00,
        }

        serializer = PromotionCarSerializer(data=data)
        assert serializer.is_valid()
        instance = serializer.save()
        assert instance.promotion.name != "Новое название"
