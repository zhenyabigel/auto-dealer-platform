import pytest

from autodealer_backend.cars.tests.factories.car_model_factory import CarModelFactory
from autodealer_backend.deals.serializers import OfferSerializer
from autodealer_backend.users.tests.factories.user_factory import (
    CustomerUserFactory,
    DealerUserFactory,
)


@pytest.mark.django_db
class TestOfferSerializer:
    def test_serializer_valid_data(self):
        customer = CustomerUserFactory()
        car_model = CarModelFactory()
        dealer = DealerUserFactory()

        data = {
            "car_model_id": car_model.id,
            "max_price": "30000.00",
            "preferred_dealer_ids": [dealer.id],
            "notes": "Test offer",
        }

        serializer = OfferSerializer(
            data=data, context={"request": type("Request", (), {"user": customer})()}
        )
        assert serializer.is_valid() is True

    def test_serializer_invalid_price(self):
        customer = CustomerUserFactory()
        car_model = CarModelFactory()

        data = {
            "car_model_id": car_model.id,
            "max_price": "-1000.00",
            "notes": "Test offer",
        }

        serializer = OfferSerializer(
            data=data, context={"request": type("Request", (), {"user": customer})()}
        )
        assert serializer.is_valid() is False
        assert "max_price" in serializer.errors

    def test_serializer_zero_price(self):
        customer = CustomerUserFactory()
        car_model = CarModelFactory()

        data = {
            "car_model_id": car_model.id,
            "max_price": "0.00",
            "notes": "Test offer",
        }

        serializer = OfferSerializer(
            data=data, context={"request": type("Request", (), {"user": customer})()}
        )
        assert serializer.is_valid() is False
        assert "max_price" in serializer.errors
