from datetime import timedelta
from decimal import Decimal

import factory
from django.utils import timezone
from faker import Faker
from users.tests.factories.customer_user_factory import CustomerUserFactory

from autodealer_backend.cars.tests.factories.car_model_factory import CarModelFactory
from autodealer_backend.deals.models.offer_model import Offer

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
    expiry_date = factory.LazyFunction(
        lambda: timezone.now() + timedelta(days=7)
    )  # ИСПРАВЛЕНО: timezone.now()
    is_active = True
