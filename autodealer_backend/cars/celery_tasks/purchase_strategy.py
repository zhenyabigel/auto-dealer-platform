import logging
import random
from datetime import timedelta
from decimal import Decimal

from django.db import models, transaction
from django.utils import timezone

from autodealer_backend.cars.models import Car, Promotion, Supplier

logger = logging.getLogger(__name__)


class PurchaseStrategy:
    def __init__(self, dealer):
        self.dealer = dealer

    @transaction.atomic
    def purchase(self):
        """Основной метод покупки автомобилей"""
        popular_brands = self.get_popular_brands()
        if not popular_brands:
            logger.warning(f"No popular brands for dealer {self.dealer.id}")
            return None

        brand = popular_brands[0]["car__brand"]
        supplier = self.find_best_supplier(brand)
        if not supplier:
            logger.warning(f"No supplier found for brand {brand}")
            return None

        # Рассчитываем итоговую цену
        final_price = self.calculate_final_price(supplier)
        if not final_price:
            logger.warning(f"Could not calculate price for supplier {supplier.id}")
            return None

        # Проверяем баланс
        if not self.validate_balance(final_price):
            logger.warning(f"Insufficient balance for dealer {self.dealer.id}")
            return None

        # Создаем автомобиль
        try:
            car = Car.objects.create(
                brand=brand,
                model=self._generate_model_name(brand),
                year=timezone.now().year,
                price=final_price,
                quantity=1,
                supplier=supplier,
                dealer=self.dealer,
                is_active=True,
            )

            # Обновляем баланс
            self.dealer.balance -= final_price
            self.dealer.save()

            logger.info(f"Purchased car {car.id} from supplier {supplier.id}")
            return car

        except Exception as e:
            logger.error(f"Error creating car: {e}")
            return None

    def validate_balance(self, required_amount):
        return self.dealer.balance >= required_amount

    def get_popular_brands(self, days=30):
        """Возвращает топ-3 самых продаваемых брендов за указанный период"""
        return (
            self.dealer.sales_history.filter(
                date__gte=timezone.now() - timedelta(days=days)
            )
            .values("car__brand")
            .annotate(total=models.Count("id"))
            .order_by("-total")[:3]
        )

    def find_best_supplier(self, brand):
        """Находит лучшего поставщика для указанного бренда"""
        return (
            Supplier.objects.filter(cars__brand=brand, is_active=True)
            .annotate(
                min_price=models.Min("cars__price"),
                discount_price=models.F("min_price")
                * (100 - models.F("discount_for_dealers"))
                / 100,
            )
            .order_by("discount_price")
            .first()
        )

    def get_active_promotions(self, supplier):
        """Возвращает активные акции для автомобилей указанного поставщика"""
        now = timezone.now()
        return Promotion.objects.filter(
            cars__supplier=supplier,  # Фильтр по поставщику через связь с Car
            dealer=self.dealer,  # Только акции текущего дилера
            start_date__lte=now,
            end_date__gte=now,
            is_active=True,
        ).distinct()

    def calculate_final_price(self, supplier):
        """Рассчитывает итоговую цену с учетом всех скидок"""
        if not supplier:
            return None

        # Получаем минимальную цену автомобиля поставщика
        min_price_result = supplier.cars.filter(is_active=True).aggregate(
            min_price=models.Min("price")
        )

        if not min_price_result["min_price"]:
            return None

        min_price = min_price_result["min_price"]

        # Скидка поставщика
        supplier_discount_price = (
            min_price * (100 - supplier.discount_for_dealers) / 100
        )

        # Максимальная акционная скидка (одним запросом)
        max_promo_result = self.get_active_promotions(supplier).aggregate(
            max_discount=models.Max("discount_percent")
        )
        max_promo_discount = max_promo_result["max_discount"] or 0

        # Итоговая цена
        final_price = supplier_discount_price * (100 - max_promo_discount) / 100
        return final_price.quantize(Decimal("0.01"))

    def _generate_model_name(self, brand):
        """Генерирует название модели в зависимости от бренда"""
        models_map = {
            "Toyota": ["Camry", "Corolla", "RAV4", "Prius"],
            "BMW": ["X5", "X3", "5 Series", "3 Series"],
            "Mercedes": ["E-Class", "C-Class", "S-Class", "GLC"],
        }
        return random.choice(models_map.get(brand, ["Unknown"]))
