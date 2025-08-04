from decimal import Decimal

import pytest

from autodealer_backend.deals.serializers import OfferSerializer
from autodealer_backend.deals.tests.factories import OfferFactory


@pytest.mark.django_db
class TestOfferSerializer:
    @pytest.fixture
    def offer(self):
        return OfferFactory()

    @pytest.fixture
    def valid_data(self, offer):
        return {
            "customer": offer.customer.id,
            "car_model": "Toyota Camry",
            "max_price": "25000.00",
            "status": "pending",
            "is_active": True,
        }

    def test_serialize_offer(self, offer):
        serializer = OfferSerializer(offer)
        assert serializer.data["id"] == offer.id
        assert serializer.data["car_model"] == offer.car_model
        assert float(serializer.data["max_price"]) == float(offer.max_price)

    def test_valid_data(self, valid_data):
        serializer = OfferSerializer(data=valid_data)
        assert serializer.is_valid()
        assert serializer.validated_data["max_price"] == Decimal("25000.00")

    def test_invalid_data(self, valid_data):
        invalid_data = valid_data.copy()
        invalid_data.update(
            {"car_model": "", "max_price": "-100.00", "status": "invalid_status"}
        )

        serializer = OfferSerializer(data=invalid_data)
        assert not serializer.is_valid()
        errors = serializer.errors
        assert "car_model" in errors
        assert "max_price" in errors
        assert "status" in errors

    def test_missing_required_fields(self):
        serializer = OfferSerializer(data={"status": "pending"})
        assert not serializer.is_valid()
        assert "customer" in serializer.errors
        assert "car_model" in serializer.errors
        assert "max_price" in serializer.errors
