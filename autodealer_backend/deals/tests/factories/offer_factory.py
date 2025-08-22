from datetime import date, timedelta
from decimal import Decimal

import factory
from faker import Faker

from autodealer_backend.cars.tests.factories.car_model_factory import CarModelFactory
from autodealer_backend.deals.models.offer_model import Offer
from autodealer_backend.users.tests.factories.user_factory import CustomerUserFactory

fake = Faker()


class OfferFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Offer
        skip_postgeneration_save = True

    customer = factory.SubFactory(CustomerUserFactory)
    car_model = factory.SubFactory(CarModelFactory)
    max_price = factory.LazyFunction(
        lambda: Decimal(
            str(fake.pydecimal(left_digits=6, right_digits=2, positive=True))
        )
    )
    status = "pending"
    expiry_date = factory.LazyFunction(lambda: date.today() + timedelta(days=7))
    is_active = True
