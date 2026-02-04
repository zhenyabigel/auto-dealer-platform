import logging
import random
import string
from datetime import timedelta
from decimal import Decimal

from celery import shared_task
from django.db import transaction
from django.db.models import Count, DecimalField, ExpressionWrapper, F
from django.utils import timezone

from autodealer_backend.cars.models import CarModel
from autodealer_backend.dealers.models import Dealer, DealerStock
from autodealer_backend.deals.models.deal_model import Deal
from autodealer_backend.suppliers.models import SupplierOffer

logger = logging.getLogger(__name__)


@shared_task
def purchase_cars_from_suppliers():
    """
    Анализ спроса и закупка авто (каждые 10 минут)
    """
    dealers = Dealer.objects.filter(is_active=True)
    now = timezone.now().date()

    logger.info(f"Запуск закупки авто для {dealers.count()} активных салонов")

    for dealer in dealers:
        try:
            _process_dealer_purchases(dealer, now)
        except Exception as e:
            logger.error(f"Ошибка при закупке для дилера {dealer.name}: {e}")


def _process_dealer_purchases(dealer, now):
    """Обработка закупок для конкретного дилера"""
    with transaction.atomic():
        dealer_refreshed = Dealer.objects.select_for_update().get(id=dealer.id)

        if not dealer.user.is_active:
            logger.info(f"Дилер {dealer.name} - не активный пользователь")
            return

        if dealer_refreshed.balance <= 0:
            logger.info(f"Дилер {dealer.name} - нулевой баланс, пропускаем")
            return

        # 1.2 Определение спроса - сначала preferred cars, потом по истории
        models_to_buy = _get_models_for_purchase(dealer_refreshed)

        if not models_to_buy:
            logger.info(f"Дилер {dealer.name} - нет моделей для закупки")
            return

        total_cost = Decimal("0")
        purchase_details = []
        purchase_budget = dealer_refreshed.balance * Decimal("0.8")  # 80% баланса

        for model_data in models_to_buy:
            if total_cost >= purchase_budget:
                break

            car_model = model_data["car_model"]
            quantity_needed = model_data["quantity_to_buy"]
            reason = model_data["reason"]

            # 1.4 Получение актуальных цен от поставщиков
            best_offer = _find_best_supplier_offer(car_model, now)
            if not best_offer:
                continue

            # 1.7 Обработка скидок и акций
            final_price = best_offer.price * (
                Decimal("1")
                - Decimal(str(best_offer.discount_percent)) / Decimal("100")
            )
            final_price = Decimal(str(final_price))

            # 1.5 Проверка баланса
            available_budget = purchase_budget - total_cost
            max_affordable = int(available_budget / final_price)
            quantity_to_buy = min(
                quantity_needed, max_affordable, best_offer.quantity_available
            )

            if quantity_to_buy <= 0:
                continue

            cost = final_price * quantity_to_buy
            total_cost += cost

            purchase_details.append(
                {
                    "car_model": car_model,
                    "supplier_offer": best_offer,
                    "quantity": quantity_to_buy,
                    "unit_price": final_price,
                    "total_cost": cost,
                    "reason": reason,
                }
            )

        # 1.6 Создание транзакции закупки
        if purchase_details:
            _execute_purchase_transaction(
                dealer_refreshed, purchase_details, total_cost
            )


def _get_models_for_purchase(dealer):
    """1.2 Определение спроса и выбор моделей для закупки"""
    models_to_buy = []

    # Первый проход: preferred cars
    preferred_models = dealer.preferred_car_models.all()
    for car_model in preferred_models:
        stock_info = _analyze_demand(dealer, car_model)
        if stock_info["need_to_buy"]:
            models_to_buy.append(
                {
                    "car_model": car_model,
                    "quantity_to_buy": stock_info["quantity_to_buy"],
                    "reason": f"Preferred car - {stock_info['reason']}",
                }
            )

    # Второй проход: на основе спроса (если preferred мало)
    if len(models_to_buy) < 3:
        demand_models = _get_models_by_demand(dealer, 5 - len(models_to_buy))
        models_to_buy.extend(demand_models)

    return models_to_buy


def _analyze_demand(dealer, car_model):
    """Анализ спроса для модели"""
    current_stock = DealerStock.objects.filter(
        dealer=dealer, car_model=car_model, is_sold=False
    ).count()

    # Продажи за последние 30 дней
    thirty_days_ago = timezone.now() - timedelta(days=30)
    sales_count = Deal.objects.filter(
        deal_type="sale",
        dealer_stock__dealer=dealer,
        dealer_stock__car_model=car_model,
        date__gte=thirty_days_ago,
        is_completed=True,
    ).count()

    # Упрощенная логика: покупаем если есть продажи и запас меньше 5
    if sales_count > 0 and current_stock < 5:
        quantity_to_buy = min(
            sales_count, 3
        )  # Покупаем столько, сколько продали, но не больше 3
        return {
            "need_to_buy": True,
            "quantity_to_buy": quantity_to_buy,
            "reason": f"есть спрос ({sales_count} продаж), запас {current_stock}",
        }
    else:
        return {
            "need_to_buy": False,
            "quantity_to_buy": 0,
            "reason": f"нет спроса или достаточный запас (продаж: {sales_count}, запас: {current_stock})",
        }


def _get_models_by_demand(dealer, limit):
    """Получение моделей для закупки на основе спроса"""
    thirty_days_ago = timezone.now() - timedelta(days=30)

    # Модели с продажами за последние 30 дней
    sold_models = (
        Deal.objects.filter(
            deal_type="sale",
            dealer_stock__dealer=dealer,
            date__gte=thirty_days_ago,
            is_completed=True,
        )
        .values("dealer_stock__car_model")
        .annotate(total_sold=Count("id"))
        .order_by("-total_sold")[: limit * 2]
    )

    models_to_buy = []
    for item in sold_models:
        try:
            car_model = CarModel.objects.get(id=item["dealer_stock__car_model"])
            if car_model in dealer.preferred_car_models.all():
                continue

            stock_info = _analyze_demand(dealer, car_model)
            if stock_info["need_to_buy"]:
                models_to_buy.append(
                    {
                        "car_model": car_model,
                        "quantity_to_buy": stock_info["quantity_to_buy"],
                        "reason": f"Demand-based - {stock_info['reason']}",
                    }
                )

            if len(models_to_buy) >= limit:
                break

        except CarModel.DoesNotExist:
            continue

    return models_to_buy


def _find_best_supplier_offer(car_model, now):
    """Поиск лучшего предложения поставщика"""
    return (
        SupplierOffer.objects.filter(
            car_model=car_model,
            is_active=True,
            quantity_available__gt=0,
            valid_from__lte=now,
            valid_to__gte=now,
        )
        .annotate(
            final_price=ExpressionWrapper(
                F("price") * (1 - F("discount_percent") / 100.0),
                output_field=DecimalField(max_digits=10, decimal_places=2),
            )
        )
        .order_by("final_price")
        .first()
    )


def _execute_purchase_transaction(dealer, purchase_details, total_cost):
    """Выполнение покупок и обновление баланса"""
    purchased_stocks = []

    for purchase in purchase_details:
        for _ in range(purchase["quantity"]):
            purchase_price = purchase["unit_price"].quantize(Decimal("0.01"))
            selling_price = (purchase["unit_price"] * Decimal("1.25")).quantize(
                Decimal("0.01")
            )

            vin = "".join(random.choices(string.ascii_uppercase + string.digits, k=17))

            stock = DealerStock.objects.create(
                dealer=dealer,
                car_model=purchase["car_model"],
                supplier=purchase["supplier_offer"].supplier,
                purchase_price=purchase_price,
                selling_price=selling_price,
                vin=vin,  # Добавляем VIN
                color="White",
                condition="new",
                arrival_date=timezone.now().date(),
                is_sold=False,
            )
            purchased_stocks.append(stock)

    dealer.balance -= total_cost
    dealer.save()

    if purchased_stocks:
        # Исправленная строка - экранируем кавычки
        details_str = ", ".join(
            [f"{p['car_model']} x{p['quantity']}" for p in purchase_details]
        )

        Deal.objects.create(
            deal_type="purchase",
            dealer=dealer.user,
            supplier_offer=purchase_details[0]["supplier_offer"],
            price=total_cost,
            quantity=len(purchased_stocks),
            is_completed=True,
            notes=f"Автоматическая закупка: {details_str}",
        )

    # Логирование
    log_message = f"Дилер {dealer.name} купил {len(purchased_stocks)} авто на сумму ${total_cost:.2f}. "
    logger.info(log_message)
