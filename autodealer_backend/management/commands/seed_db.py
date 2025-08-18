import os
import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker

fake = Faker()


class Command(BaseCommand):
    help = "Populates the database with test data"

    def handle(self, *args, **options):
        self.stdout.write("Starting database seeding...")

        with transaction.atomic():
            self._create_suppliers()
            self._create_dealers()
            self._create_cars()
            self._create_users()
            self._create_promotions()
            self._create_offers_and_deals()

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))

    def _create_suppliers(self):
        from autodealer_backend.cars.models import Supplier

        suppliers = [
            {"name": "AutoGermany", "year_established": 2005},
            {"name": "JapanMotors", "year_established": 1998},
            {"name": "ItalianCars", "year_established": 2010},
        ]
        for supplier in suppliers:
            Supplier.objects.create(
                **supplier,
                discount_for_dealers=random.choice([0, 5, 10, 15]),
                is_active=True,
            )
        self.stdout.write("Created suppliers")

    def _create_dealers(self):
        from autodealer_backend.dealers.models import Dealer

        dealers = [
            {"name": "Moscow Auto", "location": "RU"},
            {"name": "St. Petersburg Cars", "location": "RU"},
            {"name": "Kazan Motors", "location": "RU"},
        ]
        for dealer in dealers:
            Dealer.objects.create(
                **dealer,
                balance=Decimal(random.randint(100000, 500000)),
                preferred_car_brands=["Toyota", "BMW", "Mercedes"],
                preferred_car_characteristics={
                    "year__gte": 2018,
                    "engine_type": random.choice(["petrol", "diesel"]),
                },
                is_active=True,
            )
        self.stdout.write("Created dealers")

    def _create_cars(self):
        from autodealer_backend.cars.models import Car, Supplier
        from autodealer_backend.dealers.models import Dealer

        dealers = Dealer.objects.all()
        suppliers = Supplier.objects.all()

        cars_data = [
            {"brand": "Toyota", "model": "Camry", "year": 2020},
            {"brand": "BMW", "model": "X5", "year": 2021},
            {"brand": "Mercedes", "model": "E-Class", "year": 2019},
        ]

        for car_data in cars_data:
            Car.objects.create(
                **car_data,
                engine_type=random.choice(["petrol", "diesel", "hybrid"]),
                price=Decimal(random.randint(20000, 80000)),
                quantity=random.randint(1, 10),
                dealer=random.choice(dealers),
                supplier=random.choice(suppliers),
                is_active=True,
            )
        self.stdout.write("Created cars")

    def _create_users(self):
        from autodealer_backend.users.models import Customer, User

        for i in range(10):
            user = User.objects.create_user(
                email=f"username{i}@example.com",
                username=f"username{i}",
                password="testpass123",
                is_verified=True,
            )
            Customer.objects.create(
                user=user,
                balance=Decimal(random.randint(5000, 50000)),
                country="RU",
                is_active=True,
            )
        self.stdout.write("Created users and customers")

    def _create_promotions(self):
        from autodealer_backend.cars.models import Car, Promotion
        from autodealer_backend.dealers.models import Dealer

        dealers = Dealer.objects.all()
        cars = Car.objects.all()

        for i in range(5):
            promo = Promotion.objects.create(
                name=f"Promotion {i+1}",
                description=f"Special offer {i+1}",
                start_date=timezone.now() - timedelta(days=10),
                end_date=timezone.now() + timedelta(days=30),
                discount_percent=random.choice([5, 10, 15, 20]),
                dealer=random.choice(dealers),
                is_active=True,
            )
            promo.cars.set(random.sample(list(cars), min(3, len(cars))))
        self.stdout.write("Created promotions")

    def _create_offers_and_deals(self):
        from decimal import Decimal

        from autodealer_backend.cars.models import Car
        from autodealer_backend.deals.models import Deal, Offer
        from autodealer_backend.users.models import Customer

        customers = Customer.objects.all()
        cars = Car.objects.all()

        for _ in range(15):
            car = random.choice(cars)
            Offer.objects.create(
                customer=random.choice(customers),
                car_model=f"{car.brand} {car.model}",
                max_price=Decimal(car.price) * Decimal(str(random.uniform(0.8, 1.2))),
                status=random.choice(["pending", "accepted", "rejected"]),
                is_active=True,
            )

        for _ in range(10):
            car = random.choice(cars)
            Deal.objects.create(
                customer=random.choice(customers),
                dealer=car.dealer,
                car=car,
                price=car.price,
                is_active=True,
            )
        self.stdout.write("Created offers and deals")
