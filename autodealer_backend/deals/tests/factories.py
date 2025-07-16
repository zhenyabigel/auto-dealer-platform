from decimal import Decimal

import factory
from django.utils import timezone
from faker import Faker

from autodealer_backend.cars.tests.factories import CarFactory
from autodealer_backend.dealers.tests.factories import DealerFactory
from autodealer_backend.deals.models import Offer, Deal
from autodealer_backend.users.tests.factories import CustomerFactory

fake = Faker("ru_RU")


class OfferFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Offer

    customer = factory.SubFactory(CustomerFactory)
    car_model = factory.Faker('word')
    max_price = factory.LazyFunction(
        lambda: Decimal(str(round(fake.random_number(digits=5) + fake.random_number(digits=2) / 100, 2))))
    status = 'pending'
    is_active = True


class DealFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Deal

    customer = factory.SubFactory(CustomerFactory)
    dealer = factory.SubFactory(DealerFactory)
    car = factory.SubFactory(CarFactory)
    price = factory.LazyFunction(
        lambda: Decimal(str(round(fake.random_number(digits=5) + fake.random_number(digits=2) / 100, 2))))
    date = factory.LazyFunction(timezone.now)
    is_active = True
