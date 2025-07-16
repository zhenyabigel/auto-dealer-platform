import pytest

from autodealer_backend.dealers.tests.factories import DealerFactory


@pytest.mark.django_db
class TestDealerModel:
    @pytest.fixture
    def dealer(self):
        return DealerFactory(balance=10000.00)

    def test_dealer_creation(self, dealer):
        assert dealer.name is not None
        assert dealer.location is not None
        assert float(dealer.balance) >= 0
        assert isinstance(dealer.preferred_car_brands, list)
        assert isinstance(dealer.preferred_car_characteristics, dict)
        assert dealer.is_active is True
