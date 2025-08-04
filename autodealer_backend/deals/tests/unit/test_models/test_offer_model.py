from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from autodealer_backend.deals.tests.factories import OfferFactory


@pytest.mark.django_db
class TestOfferModel:
    @pytest.fixture
    def offer(self):
        return OfferFactory()

    def test_offer_creation(self, offer):
        assert offer.customer is not None
        assert offer.car_model is not None
        assert offer.max_price >= Decimal("0")
        assert offer.status == "pending"
        assert offer.is_active is True

    def test_max_price_validation(self):
        offer_test = OfferFactory.build(max_price=Decimal("-100.00"))
        with pytest.raises(ValidationError):
            offer_test.full_clean()

    def test_status_validation(self):
        offer_test = OfferFactory.build(status="invalid_status")
        with pytest.raises(ValidationError):
            offer_test.full_clean()
