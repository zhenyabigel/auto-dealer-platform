from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from autodealer_backend.users.models import Customer
from autodealer_backend.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestCustomerModel:
    @pytest.fixture
    def customer(self):
        user = UserFactory()
        return Customer.objects.create(
            user=user, balance=Decimal("1000.00"), country="US"
        )

    def test_customer_creation(self, customer):
        assert customer.user is not None
        assert customer.balance == Decimal("1000.00")
        assert customer.country == "US"
        assert customer.is_active

    def test_negative_balance_validation(self):
        user = UserFactory()
        customer = Customer(user=user, balance=Decimal("-100.00"))
        with pytest.raises(ValidationError):
            customer.full_clean()
