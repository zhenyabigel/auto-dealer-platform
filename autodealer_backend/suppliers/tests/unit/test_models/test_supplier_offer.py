import pytest

from autodealer_backend.cars.tests.factories.car_model_factory import CarModelFactory
from autodealer_backend.suppliers.tests.factories.supplier_offer_factory import (
    SupplierOfferFactory,
)


@pytest.mark.django_db
class TestSupplierOfferModel:
    def test_get_car_name_with_car_model(self):
        car_model = CarModelFactory(
            brand="Toyota", model="Camry"
        )  # Убираем generation для стабильности
        offer = SupplierOfferFactory(car_model=car_model, discount_percent=5)
        expected = f"{offer.supplier.name}: Toyota Camry - ${offer.price}"
        if offer.discount_percent > 0:
            expected += f" (-{offer.discount_percent}%)"
        assert str(offer) == expected

    def test_get_car_name_without_car_model(self):
        offer = SupplierOfferFactory(
            car_model=None, raw_brand="Honda", raw_model="Civic"
        )
        expected = f"{offer.supplier.name}: Honda Civic (raw) - ${offer.price}"
        if offer.discount_percent > 0:
            expected += f" (-{offer.discount_percent}%)"
        assert str(offer) == expected
