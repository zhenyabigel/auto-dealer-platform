# suppliers/tasks.py
from celery import shared_task
from django.utils import timezone

from autodealer_backend.cars.models import CarModel
from autodealer_backend.suppliers.models import SupplierOffer


@shared_task
def check_and_update_best_suppliers():
    """
    Каждый час проверяем, есть ли более выгодные поставщики.
    Обновляем кэш или внутренние ссылки.
    """
    now = timezone.now().date()
    car_models = CarModel.objects.filter(is_active=True)

    for car_model in car_models:
        _update_best_supplier_for_model(car_model, now)


def _update_best_supplier_for_model(car_model, now):
    active_offers = SupplierOffer.objects.filter(
        car_model=car_model,
        is_active=True,
        quantity_available__gt=0,
        valid_from__lte=now,
        valid_to__gte=now,
    )

    if not active_offers.exists():
        return

    # Вычисляем финальные цены и находим лучшее предложение
    best_offer = None
    best_price = float("inf")

    for offer in active_offers:
        # Вычисляем финальную цену с учетом скидки
        final_price = float(offer.price) * (
            1 - float(offer.discount_percent or 0) / 100.0
        )
        if final_price < best_price:
            best_price = final_price
            best_offer = offer

    if not best_offer:
        return

    # Например, можно добавить поле в DealerStock или кэшировать
    # Или обновить "рекомендованного поставщика" в кэше Redis
    from django.core.cache import cache

    cache_key = f"best_supplier:{car_model.id}"
    cache.set(
        cache_key,
        {
            "supplier_id": best_offer.supplier.id,
            "price": best_price,
            "delivery_days": best_offer.delivery_days,
        },
        timeout=3600,  # 1 час
    )
