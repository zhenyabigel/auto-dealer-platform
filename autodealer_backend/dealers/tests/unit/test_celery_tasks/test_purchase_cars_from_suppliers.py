from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from autodealer_backend.cars.tests.factories import CarModelFactory
from autodealer_backend.dealers.tasks import purchase_cars_from_suppliers
from autodealer_backend.dealers.tests.factories.dealer_factory import DealerFactory
from autodealer_backend.suppliers.tests.factories.supplier_factory import (
    SupplierFactory,
)
from autodealer_backend.suppliers.tests.factories.supplier_offer_factory import (
    SupplierOfferFactory,
)

User = get_user_model()


class TestPurchaseCarsFromSuppliers(TestCase):
    def setUp(self):
        self.dealer = DealerFactory(balance=100_000)
        self.car_model = CarModelFactory()
        self.dealer.preferred_car_models.add(self.car_model)

        self.supplier = SupplierFactory()
        self.offer = SupplierOfferFactory(
            supplier=self.supplier,
            car_model=self.car_model,
            price=20_000,
            discount_percent=10,
            quantity_available=5,
            valid_from=date.today(),
            valid_to=date.today() + date.resolution * 30,
        )

    def test_purchase_success(self):
        initial_balance = self.dealer.balance

        purchase_cars_from_suppliers()

        stock = self.dealer.dealer_stock.filter(car_model=self.car_model)
        assert stock.count() == 2
        assert all(s.purchase_price == Decimal("18000") for s in stock)

        self.dealer.refresh_from_db()
        assert self.dealer.balance == initial_balance - (18_000 * 2)

    def test_insufficient_balance_skips(self):
        self.dealer.balance = 1000
        self.dealer.save()

        purchase_cars_from_suppliers()
        assert self.dealer.dealer_stock.count() == 0

    def test_no_active_offers_skips(self):
        self.offer.is_active = False
        self.offer.save()

        purchase_cars_from_suppliers()
        assert self.dealer.dealer_stock.count() == 0

    @patch("autodealer_backend.dealers.tasks._calculate_demand", return_value=0)
    def test_no_demand_skips(self, mock_demand):
        purchase_cars_from_suppliers()
        assert self.dealer.dealer_stock.count() == 0
