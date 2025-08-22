import datetime
from datetime import date, timedelta

import pytest
from django.core.exceptions import ValidationError

from autodealer_backend.suppliers.tests.factories.supplier_factory import (
    SupplierFactory,
)
from autodealer_backend.suppliers.tests.factories.supplier_offer_factory import (
    SupplierOfferFactory,
)


@pytest.mark.django_db
class TestSupplierModel:
    def test_str_method(self):
        supplier = SupplierFactory(name="AutoImport", supplier_type="parallel")
        assert str(supplier) == "AutoImport (Параллельный импорт)"

    def test_active_offers_count_property(self):
        supplier = SupplierFactory()
        SupplierOfferFactory(
            supplier=supplier,
            is_active=True,
            valid_from=date.today(),
            valid_to=date.today() + timedelta(days=10),
        )
        SupplierOfferFactory(supplier=supplier, is_active=False)  # Не активно
        assert supplier.active_offers_count == 1

    def test_total_active_cars_property(self):
        supplier = SupplierFactory()
        SupplierOfferFactory(supplier=supplier, quantity_available=3, is_active=True)
        SupplierOfferFactory(supplier=supplier, quantity_available=2, is_active=True)
        assert supplier.total_active_cars == 5

    def test_year_established_cannot_be_future(self):
        supplier = SupplierFactory.build(
            year_established=datetime.datetime.now().year + 1
        )
        with pytest.raises(ValidationError):
            supplier.full_clean()

    def test_unique_name_constraint(self):
        SupplierFactory(name="Unique Supplier")
        with pytest.raises(Exception):
            SupplierFactory(name="Unique Supplier")
