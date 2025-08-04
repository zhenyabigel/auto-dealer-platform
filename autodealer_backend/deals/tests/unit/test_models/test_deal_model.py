from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from autodealer_backend.deals.tests.factories import DealFactory


@pytest.mark.django_db
class TestDealModel:
    @pytest.fixture
    def deal(self):
        return DealFactory()

    def test_deal_creation(self, deal):
        assert deal.customer is not None
        assert deal.dealer is not None
        assert deal.car is not None
        assert deal.price >= Decimal("0")
        assert deal.is_active is True

    def test_price_validation(self):
        deal_test = DealFactory.build(price=Decimal("-100.00"))
        with pytest.raises(ValidationError):
            deal_test.full_clean()
