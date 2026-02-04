from decimal import Decimal

import pytest
from users.tests.factories.dealer_user_factory import DealerUserFactory

from autodealer_backend.dealers.models import Dealer
from autodealer_backend.dealers.serializers import DealerSerializer


@pytest.mark.django_db
class TestDealerSerializer:
    def test_serializer_valid_data(self):
        dealer_user = DealerUserFactory(role="dealer")

        valid_data = {
            "user": dealer_user.id,
            "name": "Test Dealer Inc.",
            "legal_name": "Test Dealer Incorporated LLC",
            "dealer_type": "premium",
            "location": "US",
            "address": "123 Test Street, Test City",
            "phone": "+1234567890",
            "email": "test@dealer.com",
            "website": "https://testdealer.com",
            "contact_person": "John Doe",
            "balance": "100000.00",
            "is_active": True,
        }

        serializer = DealerSerializer(data=valid_data)

        assert serializer.is_valid(), f"Serializer errors: {serializer.errors}"

    def test_serializer_create(self):
        dealer_user = DealerUserFactory(role="dealer")

        valid_data = {
            "user": dealer_user.id,
            "name": "New Dealer Corp.",
            "legal_name": "New Dealer Corporation LLC",
            "dealer_type": "standard",
            "location": "DE",
            "address": "456 New Street, Berlin",
            "phone": "+49123456789",
            "email": "info@newdealer.de",
            "website": "https://newdealer.de",
            "contact_person": "Hans Mueller",
            "balance": "50000.00",
            "is_active": True,
        }
        serializer = DealerSerializer(data=valid_data)
        assert serializer.is_valid(), f"Serializer errors: {serializer.errors}"
        dealer = serializer.save()

        assert dealer.id is not None
        assert dealer.name == valid_data["name"]
        assert dealer.user.id == dealer_user.id
        assert dealer.balance == Decimal(valid_data["balance"])
        assert dealer.is_active is True

        assert Dealer.objects.filter(id=dealer.id).exists()

    def test_balance_validation(self):
        dealer_user = DealerUserFactory(role="dealer")

        valid_data = {
            "user": dealer_user.id,
            "name": "Positive Balance Dealer",
            "legal_name": "Positive Balance LLC",
            "dealer_type": "premium",
            "location": "US",
            "address": "789 Balance St.",
            "phone": "+1234567890",
            "email": "balance@dealer.com",
            "website": "https://balancedealer.com",
            "contact_person": "Balance Manager",
            "balance": "1000.50",
            "is_active": True,
        }

        serializer = DealerSerializer(data=valid_data)
        assert serializer.is_valid(), f"Serializer errors: {serializer.errors}"
        assert serializer.validated_data["balance"] == Decimal("1000.50")
