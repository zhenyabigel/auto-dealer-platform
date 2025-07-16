import factory
from django_countries import countries
from faker import Faker

from autodealer_backend.dealers.models import Dealer

fake = Faker("ru_RU")


class DealerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Dealer
        django_get_or_create = ('name',)

    name = factory.LazyFunction(lambda: f"{fake.company()} Autos")
    location = factory.LazyFunction(lambda: fake.random_element(elements=list(dict(countries).keys())))
    balance = factory.LazyFunction(lambda: round(fake.random_number(digits=5) + fake.random_number(digits=2) / 100, 2))
    preferred_car_brands = factory.LazyFunction(
        lambda: ['Toyota', 'BMW']
    )
    preferred_car_characteristics = factory.LazyFunction(
        lambda: {'year__gte': 2020}
    )
