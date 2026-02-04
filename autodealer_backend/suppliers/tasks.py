import logging

from celery import shared_task
from django.db.models import F
from django.utils import timezone

from autodealer_backend.dealers.models import Dealer
from autodealer_backend.suppliers.models import SupplierOffer

logger = logging.getLogger(__name__)


@shared_task
def check_and_update_suppliers():
    """
    Задача 2: Проверка актуальности поставщиков (каждый час)
    """
    dealers = Dealer.objects.filter(is_active=True)

    logger.info(f"Запуск проверки поставщиков для {dealers.count()} салонов")

    for dealer in dealers:
        try:
            _update_dealer_suppliers(dealer)
        except Exception as e:
            logger.error(
                f"Ошибка при обновлении поставщиков для дилера {dealer.name}: {e}"
            )


def _update_dealer_suppliers(dealer):
    """2.1-2.4 Обновление списка лучших поставщиков для дилера"""
    now = timezone.now().date()
    changes_made = []

    # Анализируем все модели из предпочтений дилера
    preferred_models = dealer.preferred_car_models.all()

    for car_model in preferred_models:
        # 2.2 Анализ актуальных цен
        current_best = _get_current_best_supplier(dealer, car_model)
        new_best = _find_new_best_supplier(car_model, now)

        if new_best and new_best.supplier != current_best:
            # 2.4 Обновление поставщика
            _update_supplier_preference(dealer, car_model, new_best)

            # 2.5 Логирование изменения
            change_reason = _get_change_reason(current_best, new_best)
            changes_made.append(
                {
                    "car_model": car_model,
                    "old_supplier": current_best.supplier if current_best else None,
                    "new_supplier": new_best.supplier,
                    "reason": change_reason,
                }
            )

    if changes_made:
        log_message = f"Дилер {dealer.name} - обновлены поставщики: "
        for change in changes_made:
            log_message += (
                f"{change['car_model']}: {change['old_supplier']} -> "
                f"{change['new_supplier']} ({change['reason']}); "
            )
        logger.info(log_message)


def _get_current_best_supplier(dealer, car_model):
    """Получение текущего лучшего поставщика (из кэша или последней закупки)"""
    # Ищем последнюю закупку этой модели
    last_purchase = (
        dealer.dealer_stock.filter(car_model=car_model, is_sold=False)
        .order_by("-arrival_date")
        .first()
    )

    return last_purchase.supplier if last_purchase else None


def _find_new_best_supplier(car_model, now):
    """2.3 Сравнение цен и определение лучшего поставщика"""
    return (
        SupplierOffer.objects.filter(
            car_model=car_model,
            is_active=True,
            quantity_available__gt=0,
            valid_from__lte=now,
            valid_to__gte=now,
        )
        .annotate(final_price=F("price") * (1 - F("discount_percent") / 100.0))
        .order_by("final_price")
        .first()
    )


def _update_supplier_preference(dealer, car_model, supplier_offer):
    """Обновление предпочтений поставщика"""
    # Здесь можно сохранить в отдельную модель SupplierPreference
    # или использовать кэш Redis
    from django.core.cache import cache

    cache_key = f"dealer_{dealer.id}_best_supplier_{car_model.id}"
    cache.set(
        cache_key,
        {
            "supplier_id": supplier_offer.supplier.id,
            "supplier_name": supplier_offer.supplier.name,
            "price": float(supplier_offer.price),
            "final_price": float(supplier_offer.final_price),
            "discount_percent": supplier_offer.discount_percent,
            "updated_at": timezone.now().isoformat(),
        },
        timeout=3600,  # 1 час
    )


def _get_change_reason(old_offer, new_offer):
    """2.5 Определение причины изменения поставщика"""
    if not old_offer:
        return "первый выбор поставщика"

    old_price = old_offer.price * (1 - old_offer.discount_percent / 100.0)
    new_price = new_offer.price * (1 - new_offer.discount_percent / 100.0)

    price_diff = old_price - new_price
    price_diff_percent = (price_diff / old_price) * 100

    if new_offer.discount_percent > old_offer.discount_percent:
        return f"акция (+{new_offer.discount_percent - old_offer.discount_percent}% скидка)"
    elif price_diff_percent > 5:
        return f"ниже цена (-{price_diff_percent:.1f}%)"
    else:
        return "более выгодные условия"


@shared_task
def cleanup_supplier_offers():
    """Ежедневная очистка старых неактивных офферов поставщиков"""
    from django.utils import timezone

    month_ago = timezone.now() - timezone.timedelta(days=30)
    deleted_count = SupplierOffer.objects.filter(
        is_active=False, updated_at__lt=month_ago
    ).delete()[0]

    logger.info(f"Удалено {deleted_count} старых офферов поставщиков")
