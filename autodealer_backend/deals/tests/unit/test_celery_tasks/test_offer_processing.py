from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from autodealer_backend.cars.tests.factories.car_model_factory import CarModelFactory
from autodealer_backend.dealers.tests.factories.dealer_factory import DealerFactory
from autodealer_backend.dealers.tests.factories.dealer_stock_factory import (
    DealerStockFactory,
)
from autodealer_backend.deals.tasks import _try_match_offer, process_pending_offers
from autodealer_backend.deals.tests.factories.offer_factory import OfferFactory
from autodealer_backend.users.tests.factories.user_factory import (
    CustomerUserFactory,
    DealerUserFactory,
)


@pytest.mark.django_db
class TestOfferProcessingTask:
    def test_process_pending_offers_finds_matching_stock(self):
        # Создаем данные
        customer = CustomerUserFactory(balance=Decimal("50000"))
        car_model = CarModelFactory()
        dealer_user = DealerUserFactory()
        dealer = DealerFactory(user=dealer_user)

        # Создаем оффер
        offer = OfferFactory(
            customer=customer,
            car_model=car_model,
            max_price=Decimal("30000"),
            status="pending",
            is_active=True,
            expiry_date=timezone.now() + timedelta(days=7),
        )

        # Создаем подходящий автомобиль в наличии
        stock = DealerStockFactory(
            dealer=dealer,
            car_model=car_model,
            selling_price=Decimal("25000"),
            is_sold=False,
        )

        # Выполняем задачу
        process_pending_offers()

        # Проверяем результаты
        offer.refresh_from_db()
        stock.refresh_from_db()
        customer.refresh_from_db()

        assert offer.status == "accepted"
        assert offer.is_active is False
        assert stock.is_sold is True
        assert customer.balance == Decimal("25000")  # 50000 - 25000

        # Проверяем, что создана сделка
        assert offer.deals.count() == 1
        deal = offer.deals.first()
        assert deal.deal_type == "sale"
        assert deal.price == Decimal("25000")
        assert deal.is_completed is True

    def test_process_pending_offers_insufficient_balance(self):
        # Создаем данные с недостаточным балансом
        customer = CustomerUserFactory(balance=Decimal("10000"))
        car_model = CarModelFactory()
        dealer_user = DealerUserFactory()
        dealer = DealerFactory(user=dealer_user)

        offer = OfferFactory(
            customer=customer,
            car_model=car_model,
            max_price=Decimal("30000"),
            status="pending",
            is_active=True,
            expiry_date=timezone.now() + timedelta(days=7),
        )

        # Создаем автомобиль дороже баланса клиента
        stock = DealerStockFactory(
            dealer=dealer,
            car_model=car_model,
            selling_price=Decimal("25000"),
            is_sold=False,
        )

        # Выполняем задачу
        process_pending_offers()

        # Проверяем, что ничего не изменилось
        offer.refresh_from_db()
        stock.refresh_from_db()
        customer.refresh_from_db()

        assert offer.status == "pending"  # Не изменился
        assert stock.is_sold is False  # Не продан
        assert customer.balance == Decimal("10000")  # Не изменился
        assert offer.deals.count() == 0  # Нет сделок

    def test_process_pending_offers_expired_offer(self):
        customer = CustomerUserFactory(balance=Decimal("50000"))
        car_model = CarModelFactory()
        dealer_user = DealerUserFactory()
        dealer = DealerFactory(user=dealer_user)

        # Создаем истекший оффер
        offer = OfferFactory(
            customer=customer,
            car_model=car_model,
            max_price=Decimal("30000"),
            status="pending",
            is_active=True,
            expiry_date=timezone.now() - timedelta(days=1),  # Истекший
        )

        stock = DealerStockFactory(
            dealer=dealer,
            car_model=car_model,
            selling_price=Decimal("25000"),
            is_sold=False,
        )

        process_pending_offers()

        # Проверяем, что истекший оффер игнорируется
        offer.refresh_from_db()
        stock.refresh_from_db()

        assert offer.status == "pending"
        assert stock.is_sold is False
        assert offer.deals.count() == 0

    def test_process_pending_offers_inactive_offer(self):
        customer = CustomerUserFactory(balance=Decimal("50000"))
        car_model = CarModelFactory()
        dealer_user = DealerUserFactory()
        dealer = DealerFactory(user=dealer_user)

        # Создаем неактивный оффер
        offer = OfferFactory(
            customer=customer,
            car_model=car_model,
            max_price=Decimal("30000"),
            status="pending",
            is_active=False,  # Неактивный
            expiry_date=timezone.now() + timedelta(days=7),
        )

        stock = DealerStockFactory(
            dealer=dealer,
            car_model=car_model,
            selling_price=Decimal("25000"),
            is_sold=False,
        )

        process_pending_offers()

        # Проверяем, что неактивный оффер игнорируется
        offer.refresh_from_db()
        stock.refresh_from_db()

        assert offer.status == "pending"
        assert stock.is_sold is False
        assert offer.deals.count() == 0

    def test_process_pending_offers_already_sold_car(self):
        customer = CustomerUserFactory(balance=Decimal("50000"))
        car_model = CarModelFactory()

        offer = OfferFactory(
            customer=customer,
            car_model=car_model,
            max_price=Decimal("30000"),
            status="pending",
            is_active=True,
            expiry_date=timezone.now() + timedelta(days=7),
        )

        # Создаем уже проданный автомобиль
        stock = DealerStockFactory(
            car_model=car_model,
            selling_price=Decimal("25000"),
            is_sold=True,  # Уже продан
        )

        process_pending_offers()

        # Проверяем, что проданный автомобиль игнорируется
        offer.refresh_from_db()
        stock.refresh_from_db()

        assert offer.status == "pending"
        assert stock.is_sold is True  # Остался проданным
        assert offer.deals.count() == 0

    def test_process_pending_offers_preferred_dealers(self):
        customer = CustomerUserFactory(balance=Decimal("50000"))
        car_model = CarModelFactory()
        dealer_user1 = DealerUserFactory()
        dealer_user2 = DealerUserFactory()
        dealer1 = DealerFactory(user=dealer_user1)
        dealer2 = DealerFactory(user=dealer_user2)

        offer = OfferFactory(
            customer=customer,
            car_model=car_model,
            max_price=Decimal("30000"),
            status="pending",
            is_active=True,
            expiry_date=timezone.now() + timedelta(days=7),
        )
        # Добавляем предпочтительного дилера
        offer.preferred_dealers.add(dealer_user1)

        # Создаем автомобили у обоих дилеров
        stock1 = DealerStockFactory(
            dealer=dealer1,
            car_model=car_model,
            selling_price=Decimal("25000"),
            is_sold=False,
        )
        stock2 = DealerStockFactory(
            dealer=dealer2,
            car_model=car_model,
            selling_price=Decimal("24000"),  # Дешевле, но от другого дилера
            is_sold=False,
        )

        process_pending_offers()

        # Проверяем, что выбран автомобиль от предпочтительного дилера
        offer.refresh_from_db()
        stock1.refresh_from_db()
        stock2.refresh_from_db()

        assert offer.status == "accepted"
        assert stock1.is_sold is True  # От предпочтительного дилера
        assert stock2.is_sold is False  # От другого дилера - не выбран
        assert offer.deals.count() == 1
        deal = offer.deals.first()
        assert deal.price == Decimal("25000")

    def test_try_match_offer_creates_only_one_deal(self):
        customer = CustomerUserFactory(balance=Decimal("100000"))
        car_model = CarModelFactory()
        dealer_user = DealerUserFactory()
        dealer = DealerFactory(user=dealer_user)

        offer = OfferFactory(
            customer=customer,
            car_model=car_model,
            max_price=Decimal("30000"),
            status="pending",
            is_active=True,
            expiry_date=timezone.now() + timedelta(days=7),
        )

        # Создаем несколько подходящих автомобилей
        stock1 = DealerStockFactory(
            dealer=dealer,
            car_model=car_model,
            selling_price=Decimal("25000"),
            is_sold=False,
        )
        stock2 = DealerStockFactory(
            dealer=dealer,
            car_model=car_model,
            selling_price=Decimal("26000"),
            is_sold=False,
        )

        # Вызываем функцию напрямую
        _try_match_offer(offer)

        # Проверяем, что создана только одна сделка
        offer.refresh_from_db()
        stock1.refresh_from_db()
        stock2.refresh_from_db()

        assert offer.status == "accepted"
        assert offer.deals.count() == 1
        # Один из автомобилей должен быть продан (первый найденный)
        assert stock1.is_sold is True or stock2.is_sold is True
        # Другой должен остаться непроданным
        assert stock1.is_sold is False or stock2.is_sold is False
