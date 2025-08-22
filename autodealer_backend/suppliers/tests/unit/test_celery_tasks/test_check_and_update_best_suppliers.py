# suppliers/tests/unit/test_tasks.py
from django.core.cache import cache
from django.test import TestCase

from autodealer_backend.cars.tests.factories import CarModelFactory
from autodealer_backend.suppliers.tasks import check_and_update_best_suppliers
from autodealer_backend.suppliers.tests.factories.supplier_factory import (
    SupplierFactory,
)
from autodealer_backend.suppliers.tests.factories.supplier_offer_factory import (
    SupplierOfferFactory,
)


class TestCheckAndUpdateBestSuppliers(TestCase):
    def setUp(self):
        self.car_model = CarModelFactory()
        self.supplier = SupplierFactory()
        self.offer = SupplierOfferFactory(
            supplier=self.supplier,
            car_model=self.car_model,
            price=50_000,
            discount_percent=5,
            is_active=True,
        )

    def test_best_supplier_cached(self):
        cache.clear()
        check_and_update_best_suppliers()

        cache_key = f"best_supplier:{self.car_model.id}"
        data = cache.get(cache_key)

        assert data is not None
        assert data["supplier_id"] == self.supplier.id
        assert data["price"] == 47500.0

    def test_no_active_offers_no_cache(self):
        self.offer.is_active = False
        self.offer.save()

        check_and_update_best_suppliers()

        cache_key = f"best_supplier:{self.car_model.id}"
        assert cache.get(cache_key) is None
