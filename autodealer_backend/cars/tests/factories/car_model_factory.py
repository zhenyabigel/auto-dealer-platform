import random

import factory
from faker import Faker

from autodealer_backend.cars.models import CarModel

fake = Faker("ru_RU")


class CarModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CarModel
        skip_postgeneration_save = True

    brand = factory.LazyFunction(
        lambda: random.choice(
            [
                "Toyota",
                "BMW",
                "Mercedes",
                "Honda",
                "Ford",
                "Audi",
                "Tesla",
                "Volkswagen",
            ]
        )
    )
    model = factory.LazyAttribute(
        lambda o: {
            "Toyota": random.choice(["Camry", "Corolla", "RAV4", "Land Cruiser"]),
            "BMW": random.choice(["X5", "X3", "3 Series", "5 Series", "7 Series"]),
            "Mercedes": random.choice(["C-Class", "E-Class", "GLC", "GLE", "S-Class"]),
            "Honda": random.choice(["Civic", "Accord", "CR-V", "Pilot"]),
            "Ford": random.choice(["Focus", "Fiesta", "Explorer", "Mustang"]),
            "Audi": random.choice(["A4", "A6", "Q5", "Q7", "A8"]),
            "Tesla": random.choice(["Model X"]),
            "Volkswagen": random.choice(["Jetta", "Bora", "T4", "Passat"]),
        }[o.brand]
    )
    generation = factory.LazyFunction(
        lambda: random.choice(["", "Mk1", "Mk2", "Mk3", "2022", "2023", "2025"])
    )
    production_start = factory.LazyFunction(lambda: fake.random_int(min=2015, max=2023))
    production_end = factory.LazyFunction(
        lambda: (
            fake.random_int(min=2020, max=2025)
            if random.choice([True, False])
            else None
        )
    )
    engine_type = factory.LazyFunction(
        lambda: random.choice(["petrol", "diesel", "electric", "hybrid"])
    )
    engine_volume = factory.LazyFunction(lambda: round(random.uniform(1.5, 3.0), 1))
    power = factory.LazyFunction(lambda: fake.random_int(min=100, max=300))
    transmission = factory.LazyFunction(
        lambda: random.choice(["manual", "automatic", "robot", "cvt"])
    )
    drive_type = factory.LazyFunction(lambda: random.choice(["fwd", "rwd", "awd"]))
    fuel_consumption = factory.LazyFunction(lambda: round(random.uniform(5.0, 12.0), 1))
    length = factory.LazyFunction(lambda: fake.random_int(min=4000, max=5200))
    width = factory.LazyFunction(lambda: fake.random_int(min=1700, max=2000))
    height = factory.LazyFunction(lambda: fake.random_int(min=1400, max=1800))
    weight = factory.LazyFunction(lambda: fake.random_int(min=1300, max=2200))
    seats = factory.LazyFunction(lambda: random.choice([4, 5, 7]))
    doors = factory.LazyFunction(lambda: random.choice([2, 4, 5]))
    is_active = True

    @factory.post_generation
    def body_types(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.body_types = extracted
        else:
            self.body_types = random.sample(
                ["sedan", "hatchback", "wagon", "coupe", "convertible", "suv"],
                random.randint(1, 3),
            )
        self.save()
