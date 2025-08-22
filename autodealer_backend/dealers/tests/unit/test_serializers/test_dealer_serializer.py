# dealers/tests/unit/test_serializers/test_dealer_serializer.py
from decimal import Decimal

import pytest

from autodealer_backend.dealers.models import Dealer
from autodealer_backend.dealers.serializers import DealerSerializer
from autodealer_backend.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestDealerSerializer:
    def test_serializer_valid_data(self):
        data = {
            "name": "City Motors",
            "legal_name": "City Motors LLC",
            "dealer_type": "standard",
            "location": "US",
            "phone": "+1234567890",
            "balance": Decimal("50000.00"),
        }
        serializer = DealerSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["name"] == "City Motors"

    def test_serializer_create(self):
        user = UserFactory(role="dealer")
        data = {
            "name": "New Dealer",
            "legal_name": "New Dealer LLC",
            "dealer_type": "standard",
            "location": "US",
            "address": "123 Main St",
            "phone": "+1234567890",
            "email": "contact@newdealer.com",
            "website": "https://newdealer.com",
            "contact_person": "John Doe",
            "balance": Decimal("100000.00"),
            "is_active": True,
        }
        serializer = DealerSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        dealer = serializer.save(user=user)

        assert Dealer.objects.count() == 1
        assert dealer.user == user
        assert dealer.name == "New Dealer"
        assert dealer.balance == Decimal("100000.00")

    def test_balance_validation(self):
        data = {
            "name": "Test",
            "location": "US",
            "phone": "+123",
            "balance": Decimal("-100.00"),
            "dealer_type": "standard",
        }
        serializer = DealerSerializer(data=data)
        assert not serializer.is_valid()
        assert "balance" in serializer.errors
