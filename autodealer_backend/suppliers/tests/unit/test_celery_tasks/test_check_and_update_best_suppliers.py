from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from django.utils import timezone

from autodealer_backend.cars.tests.factories import CarModelFactory
from autodealer_backend.dealers.tests.factories.dealer_factory import DealerFactory
from autodealer_backend.suppliers.tasks import (
    _update_dealer_suppliers,
    check_and_update_suppliers,
)
from autodealer_backend.suppliers.tests.factories.supplier_factory import (
    SupplierFactory,
)
from autodealer_backend.suppliers.tests.factories.supplier_offer_factory import (
    SupplierOfferFactory,
)


@pytest.mark.django_db
class TestSupplierTasks:

    def test_check_and_update_suppliers_no_active_dealers(self):
        """Тест когда нет активных дилеров"""
        dealer = DealerFactory(is_active=False)

        result = check_and_update_suppliers.delay()
        assert result.status == "SUCCESS"

    @patch("autodealer_backend.suppliers.tasks._find_new_best_supplier")
    def test_update_dealer_suppliers_with_better_offer(self, mock_find_supplier):
        """Тест обновления поставщика при лучшем предложении"""
        dealer = DealerFactory()
        car_model = CarModelFactory()
        supplier = SupplierFactory()

        dealer.preferred_car_models.add(car_model)

        # Мокаем лучшее предложение
        mock_offer = MagicMock()
        mock_offer.supplier = supplier
        mock_offer.price = Decimal("18000")
        mock_offer.discount_percent = 15
        mock_offer.final_price = Decimal("15300")
        mock_find_supplier.return_value = mock_offer

        _update_dealer_suppliers(dealer)

        # Проверяем, что информация сохранена в кэше
        from django.core.cache import cache

        cache_key = f"dealer_{dealer.id}_best_supplier_{car_model.id}"
        cached_data = cache.get(cache_key)
        assert cached_data is not None
        assert cached_data["supplier_id"] == supplier.id

    def test_find_new_best_supplier_with_discount(self):
        """Тест поиска лучшего поставщика со скидкой"""
        from autodealer_backend.suppliers.tasks import _find_new_best_supplier

        car_model = CarModelFactory()
        supplier = SupplierFactory()

        # Создаем предложение поставщика со скидкой
        SupplierOfferFactory(
            supplier=supplier,
            car_model=car_model,
            price=Decimal("20000"),
            discount_percent=20,
        )

        best_offer = _find_new_best_supplier(car_model, timezone.now().date())

        assert best_offer is not None
        assert best_offer.supplier == supplier
        assert best_offer.discount_percent == 20

    def test_find_new_best_supplier_no_offers(self):
        """Тест поиска поставщика когда нет предложений"""
        from autodealer_backend.suppliers.tasks import _find_new_best_supplier

        car_model = CarModelFactory()

        best_offer = _find_new_best_supplier(car_model, timezone.now().date())

        assert best_offer is None

    def test_get_change_reason_price_difference(self):
        """Тест определения причины изменения поставщика"""
        from autodealer_backend.suppliers.tasks import _get_change_reason

        # Создаем моки предложений
        old_offer = MagicMock()
        old_offer.price = Decimal("20000")
        old_offer.discount_percent = 0

        new_offer = MagicMock()
        new_offer.price = Decimal("18000")
        new_offer.discount_percent = 0

        reason = _get_change_reason(old_offer, new_offer)
        assert "ниже цена" in reason

    def test_get_change_reason_discount(self):
        """Тест определения причины изменения из-за скидки"""
        from autodealer_backend.suppliers.tasks import _get_change_reason

        old_offer = MagicMock()
        old_offer.price = Decimal("20000")
        old_offer.discount_percent = 0

        new_offer = MagicMock()
        new_offer.price = Decimal("20000")
        new_offer.discount_percent = 15

        reason = _get_change_reason(old_offer, new_offer)
        assert "акция" in reason
