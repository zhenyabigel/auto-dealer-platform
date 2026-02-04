from datetime import date
from decimal import Decimal

import factory
from faker import Faker

from autodealer_backend.cars.tests.factories.car_model_factory import CarModelFactory
from autodealer_backend.dealers.models import DealerStock
from autodealer_backend.dealers.tests.factories.dealer_factory import DealerFactory
from autodealer_backend.suppliers.tests.factories.supplier_factory import (
    SupplierFactory,
)

fake = Faker()


class DealerStockFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DealerStock
        skip_postgeneration_save = True

    dealer = factory.SubFactory(DealerFactory)
    car_model = factory.SubFactory(CarModelFactory)
    supplier = factory.SubFactory(SupplierFactory)

    purchase_price = factory.LazyFunction(
        lambda: Decimal(
            str(
                round(
                    fake.pydecimal(
                        left_digits=5,
                        right_digits=2,
                        positive=True,
                        min_value=10000,
                        max_value=50000,
                    ),
                    2,
                )
            )
        )
    )

    selling_price = factory.LazyAttribute(
        lambda o: (o.purchase_price * Decimal("1.2")).quantize(Decimal("0.01"))
    )

    vin = factory.LazyFunction(lambda: fake.unique.lexify(text="?" * 17).upper())
    mileage = 0
    color = factory.LazyFunction(lambda: fake.color_name())
    condition = "new"
    is_sold = False
    arrival_date = date.today()
    is_active = True
