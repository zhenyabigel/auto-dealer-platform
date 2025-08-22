# deals/tasks.py
from celery import shared_task
from django.db import transaction
from django.utils import timezone

from autodealer_backend.dealers.models import DealerStock
from autodealer_backend.deals.models.deal_model import Deal
from autodealer_backend.deals.models.offer_model import Offer
from autodealer_backend.users.models import User


@shared_task
def process_pending_offers():
    """
    Каждые 5 минут ищем подходящие авто для офферов.
    Проверяем: модель, цена, наличие, баланс.
    """
    pending_offers = Offer.objects.filter(
        status="pending",
        is_active=True,
        expiry_date__gt=timezone.now(),
    )

    for offer in pending_offers:
        _try_match_offer(offer)


@transaction.atomic
def _try_match_offer(offer):
    # Фильтруем по дилерам, если указаны
    dealers = User.objects.filter(role="dealer")
    if offer.preferred_dealers.exists():
        dealers = dealers & offer.preferred_dealers.all()

    # Находим авто
    available_stock = DealerStock.objects.filter(
        car_model=offer.car_model,
        is_sold=False,
        selling_price__lte=offer.max_price,
        dealer__user__in=dealers,
    ).select_related("dealer", "dealer__user")

    for stock in available_stock:
        customer = offer.customer
        if customer.balance < stock.selling_price:
            continue

        # Совершаем сделку
        stock.is_sold = True
        stock.save()

        Deal.objects.create(
            deal_type="sale",
            offer=offer,
            dealer_stock=stock,
            customer=customer,
            price=stock.selling_price,
            quantity=1,
            is_completed=True,
        )

        # Списываем деньги
        customer.balance -= stock.selling_price
        customer.save()

        # Обновляем статус оффера
        offer.status = "accepted"
        offer.is_active = False
        offer.save()

        # Можно отправить email
        break  # Одно авто — один оффер
