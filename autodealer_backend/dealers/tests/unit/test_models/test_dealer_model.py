from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from autodealer_backend.dealers.tests.factories.dealer_factory import DealerFactory
from autodealer_backend.dealers.tests.factories.dealer_stock_factory import (
    DealerStockFactory,
)


@pytest.mark.django_db
class TestDealerModel:
    def test_str_method(self):
        dealer = DealerFactory(name="Best Cars", location="US")
        assert str(dealer) == "Best Cars (US)"

    def test_stock_count_property(self):
        dealer = DealerFactory()
        DealerStockFactory(dealer=dealer, is_sold=False)
        DealerStockFactory(dealer=dealer, is_sold=True)
        assert dealer.stock_count == 1

    def test_total_stock_value_property(self):
        dealer = DealerFactory()
        DealerStockFactory(
            dealer=dealer,
            purchase_price=Decimal("23000.00"),
            selling_price=Decimal("25000.00"),
            is_sold=False,
        )
        DealerStockFactory(
            dealer=dealer,
            purchase_price=Decimal("23000.00"),
            selling_price=Decimal("30000.00"),
            is_sold=False,
        )
        assert dealer.total_stock_value == Decimal("55000.00")

    def test_balance_cannot_be_negative(self):
        dealer = DealerFactory()
        dealer.balance = Decimal("-100.00")
        with pytest.raises(ValidationError):
            dealer.full_clean()

    def test_unique_name_constraint(self):
        DealerFactory(name="Unique Dealer")
        with pytest.raises(Exception):
            DealerFactory(name="Unique Dealer")
