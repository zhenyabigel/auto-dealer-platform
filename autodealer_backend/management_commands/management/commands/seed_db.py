import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker

fake = Faker("ru_RU")  # Русская локализация


class Command(BaseCommand):
    help = "Populates the database with test data"

    def handle(self, *args, **options):
        self.stdout.write("Starting database seeding...")

        with transaction.atomic():
            self._create_users()
            self._create_suppliers()
            self._create_car_models()
            self._create_car_features()
            self._create_dealers()
            self._create_supplier_offers()
            self._create_dealer_stock()
            self._create_promotions()
            self._create_offers()
            self._create_deals()

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))

    def _create_users(self):
        from autodealer_backend.users.models import User

        # Создаем пользователей с определенными ролями
        roles = ["customer", "dealer", "supplier"]

        for i in range(15):  # Увеличим количество пользователей
            role = roles[i % 3]  # Распределяем роли по кругу

            User.objects.create_user(
                email=f"{role}{i}@example.com",
                username=f"{role}{i}",
                password="testpass123",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                phone=fake.phone_number()[:20],
                country="RU",
                address=fake.address(),
                balance=Decimal(random.randint(5000, 50000)),
                role=role,  # Явно указываем роль
                is_verified=True,
                is_active=True,
            )
        self.stdout.write("Created users")

    def _create_suppliers(self):
        from autodealer_backend.suppliers.models import Supplier
        from autodealer_backend.users.models import User

        suppliers_data = [
            {"name": "AutoGermany", "legal_name": "ООО АвтоГермания"},
            {"name": "JapanMotors", "legal_name": "ООО ЯпонияМоторс"},
            {"name": "ItalianCars", "legal_name": "ООО ИталияКарс"},
        ]

        supplier_users = User.objects.filter(role="supplier")[:3]

        for i, supplier_data in enumerate(suppliers_data):
            user = supplier_users[i] if i < len(supplier_users) else None
            Supplier.objects.create(
                **supplier_data,
                user=user,
                supplier_type=random.choice(["official", "parallel", "used"]),
                year_established=random.randint(1990, 2020),
                country=(
                    "DE"
                    if "Germany" in supplier_data["name"]
                    else "JP" if "Japan" in supplier_data["name"] else "IT"
                ),
                city=fake.city(),
                address=fake.address(),
                phone=fake.phone_number()[:20],
                email=fake.email(),
                website=fake.url(),
                contact_person=fake.name(),
                average_delivery_time=random.randint(7, 30),
                discount_for_dealers=random.choice([0, 5, 10, 15]),
                is_active=True,
            )
        self.stdout.write("Created suppliers")

    def _create_car_models(self):
        from autodealer_backend.cars.models import CarModel

        car_models_data = [
            {"brand": "Toyota", "model": "Camry", "generation": "XV70"},
            {"brand": "BMW", "model": "X5", "generation": "G05"},
            {"brand": "Mercedes", "model": "E-Class", "generation": "W213"},
            {"brand": "Audi", "model": "A6", "generation": "C8"},
            {"brand": "Volkswagen", "model": "Passat", "generation": "B8"},
            {"brand": "Honda", "model": "Accord", "generation": "10th"},
            {"brand": "Hyundai", "model": "Sonata", "generation": "DN8"},
            {"brand": "Kia", "model": "Optima", "generation": "JF"},
            {"brand": "Skoda", "model": "Superb", "generation": "3V"},
            {"brand": "Ford", "model": "Mondeo", "generation": "5th"},
        ]

        for car_data in car_models_data:
            CarModel.objects.create(
                **car_data,
                production_start=random.randint(2015, 2023),
                production_end=(
                    random.randint(2020, 2025) if random.choice([True, False]) else None
                ),
                engine_type=random.choice(["petrol", "diesel", "electric", "hybrid"]),
                engine_volume=Decimal(random.uniform(1.5, 3.0)),
                power=random.randint(100, 300),
                transmission=random.choice(["manual", "automatic", "robot", "cvt"]),
                drive_type=random.choice(["fwd", "rwd", "awd"]),
                fuel_consumption=Decimal(random.uniform(5.0, 12.0)),
                length=random.randint(4500, 5000),
                width=random.randint(1800, 1900),
                height=random.randint(1400, 1500),
                weight=random.randint(1400, 1800),
                body_types=random.sample(
                    ["sedan", "hatchback", "wagon", "coupe", "convertible"],
                    random.randint(1, 3),
                ),
                seats=random.choice([4, 5, 7]),
                doors=random.choice([2, 4, 5]),
                is_active=True,
            )
        self.stdout.write("Created car models")

    def _create_car_features(self):
        from autodealer_backend.cars.models import CarFeature, CarModel

        features_data = [
            {"category": "safety", "name": "ABS", "is_standard": True},
            {"category": "safety", "name": "ESP", "is_standard": True},
            {"category": "comfort", "name": "Климат-контроль", "is_standard": False},
            {"category": "comfort", "name": "Подогрев сидений", "is_standard": False},
            {"category": "multimedia", "name": "Навигация", "is_standard": False},
            {"category": "multimedia", "name": "Apple CarPlay", "is_standard": False},
            {"category": "exterior", "name": "Светодиодные фары", "is_standard": False},
            {"category": "exterior", "name": "Панорамная крыша", "is_standard": False},
            {"category": "interior", "name": "Кожаный салон", "is_standard": False},
            {
                "category": "interior",
                "name": "Электропривод сидений",
                "is_standard": False,
            },
        ]

        car_models = CarModel.objects.all()

        for car_model in car_models:
            for feature_data in random.sample(features_data, random.randint(3, 8)):
                CarFeature.objects.create(
                    car_model=car_model,
                    **feature_data,
                    description=fake.sentence(),
                    is_optional=not feature_data["is_standard"],
                )
        self.stdout.write("Created car features")

    def _create_dealers(self):
        from autodealer_backend.cars.models import CarModel
        from autodealer_backend.dealers.models import Dealer
        from autodealer_backend.users.models import User

        dealers_data = [
            {"name": "Московский Автоцентр", "legal_name": "ООО Московский Автоцентр"},
            {
                "name": "Петербургские Автомобили",
                "legal_name": "ООО Петербургские Автомобили",
            },
            {"name": "Казанский Автодом", "legal_name": "ООО Казанский Автодом"},
        ]

        dealer_users = User.objects.filter(role="dealer")[:3]
        car_models = list(CarModel.objects.all())

        for i, dealer_data in enumerate(dealers_data):
            user = dealer_users[i] if i < len(dealer_users) else None
            dealer = Dealer.objects.create(
                **dealer_data,
                user=user,
                dealer_type=random.choice(["premium", "standard", "discount"]),
                location="RU",
                address=fake.address(),
                phone=fake.phone_number()[:20],
                email=fake.email(),
                website=fake.url(),
                contact_person=fake.name(),
                balance=Decimal(random.randint(100000, 500000)),
                is_active=True,
            )
            # Добавляем предпочитаемые модели
            dealer.preferred_car_models.set(
                random.sample(car_models, random.randint(2, 5))
            )
        self.stdout.write("Created dealers")

    def _create_supplier_offers(self):
        from autodealer_backend.cars.models import CarModel
        from autodealer_backend.suppliers.models import Supplier, SupplierOffer

        suppliers = Supplier.objects.all()
        car_models = CarModel.objects.all()

        for supplier in suppliers:
            for _ in range(random.randint(3, 8)):
                car_model = random.choice(car_models)
                SupplierOffer.objects.create(
                    supplier=supplier,
                    car_model=car_model,
                    price=Decimal(random.randint(15000, 60000)),
                    quantity_available=random.randint(1, 20),
                    discount_percent=random.choice([0, 5, 10]),
                    valid_from=timezone.now() - timedelta(days=10),
                    valid_to=timezone.now() + timedelta(days=60),
                    delivery_days=random.randint(7, 30),
                    is_new=random.choice([True, False]),
                    warranty_months=random.choice([12, 24, 36]),
                    is_active=True,
                )
        self.stdout.write("Created supplier offers")

    def _create_dealer_stock(self):
        from autodealer_backend.cars.models import CarModel
        from autodealer_backend.dealers.models import Dealer, DealerStock
        from autodealer_backend.suppliers.models import SupplierOffer

        dealers = Dealer.objects.all()
        car_models = CarModel.objects.all()
        supplier_offers = SupplierOffer.objects.all()

        for dealer in dealers:
            for _ in range(random.randint(5, 15)):
                car_model = random.choice(car_models)
                supplier_offer = (
                    random.choice(supplier_offers) if supplier_offers.exists() else None
                )

                purchase_price = Decimal(random.randint(18000, 65000))
                selling_price = purchase_price * Decimal("1.2")  # 20% наценка

                DealerStock.objects.create(
                    dealer=dealer,
                    car_model=car_model,
                    supplier=supplier_offer.supplier if supplier_offer else None,
                    purchase_price=purchase_price,
                    selling_price=selling_price,
                    vin=fake.unique.bothify("?????????????????").upper(),
                    mileage=(
                        0
                        if random.choice([True, False])
                        else random.randint(1000, 50000)
                    ),
                    color=random.choice(
                        ["black", "white", "silver", "blue", "red", "green"]
                    ),
                    condition=random.choice(["new", "used", "demo"]),
                    is_sold=False,
                    arrival_date=timezone.now() - timedelta(days=random.randint(1, 30)),
                    is_active=True,
                )
        self.stdout.write("Created dealer stock")

    def _create_promotions(self):
        from autodealer_backend.cars.models import CarModel
        from autodealer_backend.dealers.models import Dealer
        from autodealer_backend.promotion.models.promotion_car_model import PromotionCar
        from autodealer_backend.promotion.models.promotion_model import Promotion

        dealers = Dealer.objects.all()
        car_models = CarModel.objects.all()

        for i in range(5):
            promotion = Promotion.objects.create(
                name=f"Акция {i + 1} - {fake.word().title()}",
                description=fake.text(),
                promotion_type=random.choice(["supplier", "dealer"]),
                start_date=timezone.now() - timedelta(days=10),
                end_date=timezone.now() + timedelta(days=30),
                discount_percent=random.choice([5, 10, 15, 20]),
                max_discount_amount=Decimal(random.randint(5000, 20000)),
                dealer=random.choice(dealers) if random.choice([True, False]) else None,
                is_active=True,
            )

            # Добавляем автомобили в акцию
            selected_car_models = random.sample(
                list(car_models), min(3, len(car_models))
            )
            for car_model in selected_car_models:
                PromotionCar.objects.create(
                    promotion=promotion,
                    car_model=car_model,
                    special_price=(
                        Decimal(random.randint(15000, 70000))
                        if random.choice([True, False])
                        else None
                    ),
                )
        self.stdout.write("Created promotions")

    def _create_offers(self):
        from autodealer_backend.cars.models import CarModel
        from autodealer_backend.dealers.models import Dealer
        from autodealer_backend.deals.models.offer_model import Offer
        from autodealer_backend.users.models import User

        customers = User.objects.filter(role="customer")
        car_models = CarModel.objects.all()
        dealers = Dealer.objects.all()

        for _ in range(10):
            car_model = random.choice(car_models)

            # Сначала создаем оффер без preferred_dealers
            offer = Offer.objects.create(
                customer=random.choice(customers),
                car_model=car_model,
                max_price=Decimal(random.randint(20000, 80000)),
                status=random.choice(["pending", "accepted", "rejected"]),
                expiry_date=timezone.now() + timedelta(days=random.randint(1, 30)),
                notes=fake.sentence(),
                is_active=True,
            )

            # Берем только существующих дилеров и получаем их пользователей
            if dealers.exists():
                selected_dealers = random.sample(list(dealers), min(3, dealers.count()))
                # Получаем user_id из связанных дилеров
                dealer_user_ids = [
                    dealer.user_id for dealer in selected_dealers if dealer.user_id
                ]

                if dealer_user_ids:
                    offer.preferred_dealers.set(dealer_user_ids)

        self.stdout.write("Created offers")

    def _create_deals(self):
        from autodealer_backend.dealers.models import DealerStock
        from autodealer_backend.deals.models.deal_model import Deal
        from autodealer_backend.deals.models.offer_model import Offer
        from autodealer_backend.suppliers.models import SupplierOffer
        from autodealer_backend.users.models import User

        customers = User.objects.filter(role="customer")
        dealer_stocks = DealerStock.objects.filter(is_sold=False)
        supplier_offers = SupplierOffer.objects.filter(is_active=True)
        offers = Offer.objects.filter(status="accepted")

        # Получаем пользователей с ролью dealer, а не объекты Dealer
        dealers = User.objects.filter(role="dealer")

        # Сделки продажи (клиентам)
        for _ in range(8):
            if dealer_stocks.exists():
                stock = random.choice(dealer_stocks)
                Deal.objects.create(
                    deal_type="sale",
                    dealer_stock=stock,
                    customer=random.choice(customers),
                    price=stock.selling_price,
                    quantity=1,
                    is_completed=True,
                    notes=fake.sentence(),
                )
                stock.is_sold = True
                stock.save()

        # Сделки покупки (у поставщиков)
        for _ in range(5):
            if supplier_offers.exists() and dealers.exists():
                supplier_offer = random.choice(supplier_offers)
                Deal.objects.create(
                    deal_type="purchase",
                    dealer=random.choice(dealers),  # Теперь это User с ролью dealer
                    supplier_offer=supplier_offer,
                    price=supplier_offer.price,
                    quantity=random.randint(1, 5),
                    is_completed=True,
                    notes=f"Закупка у {supplier_offer.supplier.name}",
                )

        self.stdout.write("Created deals")
