from decimal import Decimal

import pytest

from autodealer_backend.users.serializers import CustomerSerializer
from autodealer_backend.users.tests.factories import CustomerFactory


@pytest.mark.django_db
class TestCustomerSerializer:
    @pytest.fixture
    def customer(self):
        return CustomerFactory()

    def test_serialize_customer(self, customer):
        serializer = CustomerSerializer(customer)
        assert serializer.data["id"] == customer.id
        assert serializer.data["balance"] == str(customer.balance)
        assert serializer.data["user"]["email"] == customer.user.email

    def test_update_balance(self, customer):
        serializer = CustomerSerializer(
            instance=customer, data={"balance": "2000.00"}, partial=True
        )
        assert serializer.is_valid()
        updated = serializer.save()
        assert updated.balance == Decimal("2000.00")
