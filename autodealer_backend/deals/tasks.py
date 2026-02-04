import logging
from decimal import Decimal

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from autodealer_backend.dealers.models import DealerStock
from autodealer_backend.deals.models.deal_model import Deal
from autodealer_backend.deals.models.offer_model import Offer
from autodealer_backend.users.models import User

logger = logging.getLogger(__name__)


@shared_task
def process_pending_offers():
    """
    Задача 3: Обработка Offer (покупка авто покупателем)
    """
    now = timezone.now()
    pending_offers = Offer.objects.filter(
        status="pending",
        is_active=True,
        expiry_date__gt=now,
    ).select_related("customer", "car_model")

    logger.info(f"Обработка {pending_offers.count()} ожидающих офферов")

    for offer in pending_offers:
        try:
            _process_single_offer(offer)
        except Exception as e:
            logger.error(f"Ошибка при обработке оффера {offer.id}: {e}")


@transaction.atomic
def _process_single_offer(offer):
    """Обработка одного оффера"""
    # 3.2 Проверка покупателя
    if not _validate_customer(offer.customer):
        offer.status = "rejected"
        offer.is_active = False
        offer.notes = "Покупатель не прошел проверку"
        offer.save()
        return

    # 3.3 Поиск подходящих автосалонов
    suitable_dealers = _find_suitable_dealers(offer)
    if not suitable_dealers:
        offer.notes = "Не найдено подходящих автомобилей в наличии"
        offer.save()
        return

    # 3.4 Выбор подходящего салона
    selected_dealer_stock = _select_best_dealer(offer, suitable_dealers)
    if not selected_dealer_stock:
        offer.notes = "Не удалось выбрать салон для сделки"
        offer.save()
        return

    # 3.5 Проведение сделки
    _execute_sale_transaction(offer, selected_dealer_stock)

    # 3.6 Обновление Offer
    offer.status = "accepted"
    offer.is_active = False
    offer.save()

    # 3.7 Логирование
    logger.info(
        f"Оффер {offer.id} выполнен: {offer.customer} купил {offer.car_model} "
        f"у {selected_dealer_stock.dealer.name} за ${selected_dealer_stock.selling_price}"
    )


def _validate_customer(customer):
    """3.2 Проверка покупателя"""
    return (
        customer.balance > 0
        and customer.is_active
        and customer.is_verified  # Предполагаем, что такое поле есть
    )


def _find_suitable_dealers(offer):
    """3.3 Поиск подходящих автосалонов"""
    return DealerStock.objects.filter(
        car_model=offer.car_model,
        is_sold=False,
        selling_price__lte=offer.max_price,
        dealer__is_active=True,
    ).select_related("dealer", "dealer__user")


def _select_best_dealer(offer, dealer_stocks):
    """3.4 Выбор подходящего салона по приоритету"""
    scored_dealers = []

    for stock in dealer_stocks:
        score = Decimal("0")

        # Приоритет 1: минимальная цена (50%)
        price_score = (
            (offer.max_price - stock.selling_price) / offer.max_price * Decimal("100")
        )
        score += price_score * Decimal("0.5")  # Исправлено!

        # Приоритет 2: история покупок (30%)
        if offer.customer:
            history_score = _calculate_history_score(offer.customer, stock.dealer)
            score += history_score * Decimal("0.3")  # 30% веса

        # Приоритет 3: дни в запасе (20%)
        if stock.days_in_stock > 30:
            score -= Decimal("10")  # Штраф за старый запас
        elif stock.days_in_stock < 7:
            score += Decimal("5")  # Бонус за свежий запас

        scored_dealers.append((score, stock))

    if not scored_dealers:
        return None

    # Выбираем салон с максимальным score
    scored_dealers.sort(key=lambda x: x[0], reverse=True)
    return scored_dealers[0][1]


def _calculate_history_score(customer, dealer):
    """Расчет оценки на основе истории продаж"""
    successful_deals = Deal.objects.filter(
        deal_type="sale", customer=customer, dealer=dealer.user, is_completed=True
    ).count()

    return min(successful_deals * 10, 100)  # Макс 100 баллов


def _execute_sale_transaction(offer, dealer_stock):
    """3.5 Проведение сделки"""
    # Блокируем записи для избежания race condition
    customer = User.objects.select_for_update().get(id=offer.customer.id)
    dealer = dealer_stock.dealer
    stock = DealerStock.objects.select_for_update().get(id=dealer_stock.id)

    if stock.is_sold or customer.balance < stock.selling_price:
        raise Exception("Условия сделки изменились")

    if not customer.is_verified:
        raise Exception("Покупатель не верифицирован")

    # Помечаем авто как проданное
    stock.is_sold = True
    stock.save()

    # Денежные операции
    customer.balance -= stock.selling_price
    customer.save()

    dealer.balance += stock.selling_price
    dealer.save()

    # Создаем сделку
    Deal.objects.create(
        deal_type="sale",
        offer=offer,
        dealer_stock=stock,
        customer=customer,
        dealer=dealer.user,
        price=stock.selling_price,
        quantity=1,
        is_completed=True,
        notes=f"Продажа по офферу #{offer.id}",
    )


@shared_task
def expire_old_offers():
    """Ежедневная очистка просроченных офферов"""
    from django.utils import timezone

    from autodealer_backend.deals.models.offer_model import Offer

    expired_count = Offer.objects.filter(
        status="pending", expiry_date__lte=timezone.now(), is_active=True
    ).update(status="expired", is_active=False)

    logger.info(f"Просрочено {expired_count} офферов")
