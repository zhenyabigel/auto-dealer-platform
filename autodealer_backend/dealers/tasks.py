from datetime import timedelta

from celery import shared_task
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from autodealer_backend.cars.models import CarModel
from autodealer_backend.dealers.models import Dealer, DealerStock
from autodealer_backend.deals.models.deal_model import Deal
from autodealer_backend.suppliers.models import SupplierOffer


@shared_task
def purchase_cars_from_suppliers():
    """
    Каждые 10 минут автосалоны закупают авто:
    - На основе предпочтений и спроса (истории продаж)
    - Проверка баланса
    - Учёт акций поставщиков
    """
    dealers = Dealer.objects.filter(is_active=True)
    now = timezone.now().date()

    for dealer in dealers:
        _process_dealer_purchases(dealer, now)


def _process_dealer_purchases(dealer, now):
    with transaction.atomic():
        # Определяем приоритетные модели: из предпочтений или по продажам
        preferred_models = dealer.preferred_car_models.all()
        if not preferred_models.exists():
            # Если нет предпочтений — берём топ по продажам
            top_sold = (
                Deal.objects.filter(
                    deal_type="sale",
                    dealer_stock__dealer=dealer,
                    is_completed=True,
                )
                .values("dealer_stock__car_model")
                .order_by("-quantity")[:5]
            )
            model_ids = [item["dealer_stock__car_model"] for item in top_sold]
            preferred_models = CarModel.objects.filter(id__in=model_ids)

        if not preferred_models.exists():
            return  # Нечего покупать

        total_cost = 0
        purchases = []

        for car_model in preferred_models:
            # Ищем лучшее предложение с учётом скидок
            best_offer = (
                SupplierOffer.objects.filter(
                    car_model=car_model,
                    is_active=True,
                    quantity_available__gt=0,
                    valid_from__lte=now,
                    valid_to__gte=now,
                )
                .annotate(final_price=F("price") * (1 - F("discount_percent") / 100.0))
                .order_by("final_price")  # Используем аннотированное поле
                .first()
            )

            if not best_offer:
                continue

            # Вычисляем финальную цену
            price = best_offer.price * (1 - best_offer.discount_percent / 100.0)
            quantity = _calculate_demand(dealer, car_model)  # см. ниже
            cost = price * quantity

            if dealer.balance < total_cost + cost:
                break  # Недостаточно средств

            # Создаём записи в DealerStock
            for _ in range(quantity):
                stock = DealerStock.objects.create(
                    dealer=dealer,
                    car_model=car_model,
                    supplier=best_offer.supplier,
                    purchase_price=price,
                    selling_price=price * 1.2,  # наценка 20%
                    color="White",
                    condition="new",
                    arrival_date=now,
                )
                purchases.append(stock)
                total_cost += price

        # Обновляем баланс
        if total_cost > 0:
            dealer.balance -= total_cost
            dealer.save()

            # Фиксируем сделку
            Deal.objects.create(
                deal_type="purchase",
                supplier_offer=best_offer,
                dealer=dealer.user,
                price=total_cost,
                quantity=len(purchases),
                is_completed=True,
            )


def _calculate_demand(dealer, car_model):
    """
    Простая логика: 2 авто на модель, если нет истории.
    Или +1 на каждые 5 продаж за последние 30 дней.
    """
    base_demand = 2
    recent_sales = Deal.objects.filter(
        deal_type="sale",
        dealer_stock__dealer=dealer,
        dealer_stock__car_model=car_model,
        date__gte=timezone.now() - timedelta(days=30),
    ).count()
    return base_demand + (recent_sales // 5)
