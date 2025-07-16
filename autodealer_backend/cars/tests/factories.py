import random
from datetime import timedelta

import factory
from django.utils import timezone
from faker import Faker

from autodealer_backend.cars.models import Car, Supplier, Promotion
from autodealer_backend.dealers.tests.factories import DealerFactory

fake = Faker("ru_RU")


class SupplierFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Supplier
        django_get_or_create = ('name',)
        skip_postgeneration_save = True

    name = factory.Sequence(lambda n: f"Поставщик {n}")
    year_established = factory.LazyFunction(
        lambda: fake.random_int(min=1950, max=2020)
    )
    discount_for_dealers = factory.LazyFunction(
        lambda: fake.random_int(min=0, max=30)
    )

    @classmethod
    def create_for_test(cls, **kwargs):
        defaults = {
            'name': "Тестовый поставщик",
            'year_established': 2000,
            'discount_for_dealers': 15
        }
        defaults.update(kwargs)
        return cls(**defaults)


class CarFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Car

    brand = factory.LazyFunction(
        lambda: random.choice(['Toyota', 'BMW', 'Mercedes', 'Honda', 'Ford'])
    )
    model = factory.LazyAttribute(lambda o: {
        'Toyota': random.choice(['Camry', 'Corolla', 'RAV4']),
        'BMW': random.choice(['X5', 'X3', '3 Series']),
        'Mercedes': random.choice(['C-Class', 'E-Class', 'GLC']),
        'Honda': random.choice(['Civic', 'Accord', 'CR-V']),
        'Ford': random.choice(['Focus', 'Fiesta', 'Explorer'])
    }[o.brand])
    year = factory.LazyFunction(lambda: fake.random_int(min=2000, max=2023))
    engine_type = factory.LazyFunction(
        lambda: random.choice(['petrol', 'diesel', 'electric', 'hybrid'])
    )
    price = factory.LazyFunction(
        lambda: fake.pydecimal(left_digits=5, right_digits=2, positive=True)
    )
    quantity = factory.LazyFunction(lambda: fake.random_int(min=1, max=10))
    dealer = factory.SubFactory(DealerFactory)
    supplier = factory.SubFactory(SupplierFactory)


class PromotionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Promotion
        skip_postgeneration_save = True

    name = factory.Sequence(lambda n: f"Акция {n}")
    description = factory.LazyFunction(lambda: fake.text(max_nb_chars=200))
    start_date = factory.LazyFunction(lambda: timezone.now() - timedelta(days=1))
    end_date = factory.LazyAttribute(
        lambda o: timezone.now() + timedelta(days=7)
    )
    discount_percent = factory.LazyFunction(
        lambda: fake.random_int(min=5, max=30)
    )
    dealer = factory.SubFactory(DealerFactory)

    @factory.post_generation
    def cars(self, create, extracted, **kwargs):
        if not create or extracted:
            return
        car = CarFactory(dealer=self.dealer)
        self.cars.add(car)
