from datetime import date

import pytest
from django.core.exceptions import ValidationError

from autodealer_backend.dealers.models import DealerStock
from autodealer_backend.dealers.tests.factories.dealer_stock_factory import (
    DealerStockFactory,
)


@pytest.mark.django_db
class TestDealerStockModel:
    def test_str_method(self):
        stock = DealerStockFactory(
            car_model__brand="BMW", car_model__model="X5", dealer__name="Luxury Motors"
        )
        assert str(stock) == "BMW X5 (new) - Luxury Motors"

    def test_profit_property(self):
        stock = DealerStockFactory(
            purchase_price=20000, selling_price=25000, is_sold=True
        )
        assert stock.profit == 5000

    def test_profit_zero_if_not_sold(self):
        stock = DealerStockFactory(
            purchase_price=20000, selling_price=25000, is_sold=False
        )
        assert stock.profit == 0

    def test_days_in_stock(self):
        stock = DealerStockFactory(arrival_date=date.today())
        assert stock.days_in_stock == 0

    def test_vin_unique_constraint(self):
        DealerStockFactory(vin="12345678901234567")
        with pytest.raises(Exception):
            DealerStockFactory(vin="12345678901234567")

    def test_selling_price_cannot_be_less_than_purchase(self):
        stock = DealerStock(
            car_model=DealerStockFactory.build().car_model,
            dealer=DealerStockFactory.build().dealer,
            purchase_price=30000,
            selling_price=25000,
            vin="TESTVIN1234567890",
            condition="new",
            color="White",
            arrival_date=date.today(),
        )

        with pytest.raises(ValidationError):
            stock.full_clean()
