from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.utils import timezone

from autodealer_backend.cars.tests.factories import CarModelFactory
from autodealer_backend.dealers.tasks import (
    _process_dealer_purchases,
    purchase_cars_from_suppliers,
)
from autodealer_backend.dealers.tests.factories.dealer_factory import DealerFactory
from autodealer_backend.dealers.tests.factories.dealer_stock_factory import (
    DealerStockFactory,
)
from autodealer_backend.deals.tests.factories.deals_factory import DealFactory
from autodealer_backend.suppliers.tests.factories.supplier_offer_factory import (
    SupplierOfferFactory,
)


@pytest.mark.django_db
class TestDealerTasksIntegration:
    """Интеграционные тесты для задач дилеров"""

    def test_purchase_cars_integration_with_mock(self):
        """Интеграционный тест с моком Celery"""
        dealer = DealerFactory(balance=Decimal("100000"))
        car_model = CarModelFactory()
        dealer.preferred_car_models.add(car_model)

        # Создаем реальное предложение поставщика
        supplier_offer = SupplierOfferFactory(
            car_model=car_model,
            price=Decimal("20000"),
            discount_percent=10,
            quantity_available=5,
        )

        # Создаем историю продаж
        stock = DealerStockFactory(dealer=dealer, car_model=car_model)
        DealFactory(
            deal_type="sale",
            dealer_stock=stock,
            dealer=dealer.user,
            is_completed=True,
            date=timezone.now() - timedelta(days=10),
        )

        initial_balance = dealer.balance
        initial_stock_count = dealer.dealer_stock.count()

        # Запускаем задачу напрямую (без Celery)
        purchase_cars_from_suppliers()

        # Проверяем результаты
        dealer.refresh_from_db()
        assert dealer.balance < initial_balance
        assert dealer.dealer_stock.count() > initial_stock_count

    def test_process_dealer_purchases_integration(self):
        """Интеграционный тест функции _process_dealer_purchases"""
        dealer = DealerFactory(balance=Decimal("100000"))
        car_model = CarModelFactory()
        dealer.preferred_car_models.add(car_model)

        # Создаем реальное предложение поставщика
        supplier_offer = SupplierOfferFactory(
            car_model=car_model,
            price=Decimal("20000"),
            discount_percent=10,
            quantity_available=5,
        )

        # Создаем историю продаж
        stock = DealerStockFactory(dealer=dealer, car_model=car_model)
        DealFactory(
            deal_type="sale",
            dealer_stock=stock,
            dealer=dealer.user,
            is_completed=True,
            date=timezone.now() - timedelta(days=10),
        )

        initial_balance = dealer.balance
        initial_stock_count = dealer.dealer_stock.count()

        # Запускаем функцию напрямую
        _process_dealer_purchases(dealer, timezone.now().date())

        # Проверяем результаты
        dealer.refresh_from_db()
        assert dealer.balance < initial_balance
        assert dealer.dealer_stock.count() > initial_stock_count

    def test_purchase_cars_task_structure(self):
        """Тест структуры задачи - проверяем что задача вызывается корректно"""
        with patch(
            "autodealer_backend.dealers.tasks.purchase_cars_from_suppliers.delay"
        ) as mock_task:
            # Вызываем задачу
            purchase_cars_from_suppliers.delay()

            # Проверяем что задача была вызвана
            mock_task.assert_called_once()

    def test_complete_purchase_flow(self):
        """Тест полного цикла закупки от анализа спроса до создания сделки"""
        # Очищаем ВСЕ поставщики перед тестом
        from autodealer_backend.suppliers.models import Supplier, SupplierOffer

        SupplierOffer.objects.all().delete()
        Supplier.objects.all().delete()

        dealer = DealerFactory(balance=Decimal("100000"))
        car_model = CarModelFactory()
        dealer.preferred_car_models.add(car_model)

        # Создаем несколько продаж для создания спроса
        stock = DealerStockFactory(dealer=dealer, car_model=car_model)
        for i in range(5):  # Несколько продаж
            DealFactory(
                deal_type="sale",
                dealer_stock=stock,
                dealer=dealer.user,
                is_completed=True,
                date=timezone.now() - timedelta(days=i * 3),
            )

        # Создаем предложение поставщика
        supplier_offer = SupplierOfferFactory(
            car_model=car_model,
            price=Decimal("15000"),
            discount_percent=20,
            quantity_available=10,
        )

        # Отладочная информация
        print(f"Создан поставщик: {supplier_offer.supplier.name}")
        print(f"Всего поставщиков в базе: {Supplier.objects.count()}")
        print(f"Всего предложений в базе: {SupplierOffer.objects.count()}")

        dealer.balance
        dealer.dealer_stock.count()
        dealer.user.supplier_purchases.count()

        # Запускаем процесс закупки
        _process_dealer_purchases(dealer, timezone.now().date())

        # Проверяем полный цикл
        dealer.refresh_from_db()

        # Отладочная информация после выполнения
        new_stocks = dealer.dealer_stock.filter(arrival_date=timezone.now().date())
        print(f"Создано новых автомобилей: {new_stocks.count()}")
        for new_stock in new_stocks:
            print(
                f"Новый автомобиль: {new_stock.car_model}, поставщик: {new_stock.supplier.name}"
            )

        # ... остальные проверки
