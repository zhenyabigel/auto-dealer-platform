from datetime import date, timedelta
from decimal import Decimal

import factory
from faker import Faker

from autodealer_backend.cars.tests.factories.car_model_factory import CarModelFactory
from autodealer_backend.suppliers.models import SupplierOffer
from autodealer_backend.suppliers.tests.factories.supplier_factory import (
    SupplierFactory,
)

fake = Faker()


class SupplierOfferFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SupplierOffer
        skip_postgeneration_save = True

    supplier = factory.SubFactory(SupplierFactory)  # Правильно
    car_model = factory.SubFactory(CarModelFactory)
    price = factory.LazyFunction(
        lambda: Decimal(
            str(fake.pydecimal(left_digits=6, right_digits=2, positive=True))
        )
    )
    quantity_available = 5
    discount_percent = 0
    valid_from = date.today()
    valid_to = factory.LazyFunction(lambda: date.today() + timedelta(days=30))
    delivery_days = 14
    is_new = True
    warranty_months = 24
    is_active = True
