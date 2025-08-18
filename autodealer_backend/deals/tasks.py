import logging

from celery import shared_task
from django.db.models import Count, Q
from django.utils import timezone

from autodealer_backend.deals.models import Deal, Offer

logger = logging.getLogger(__name__)


@shared_task
def process_pending_offers():
    """Обработка ожидающих предложений покупателей"""
    from autodealer_backend.cars.models import Car

    offers = Offer.objects.filter(status="pending", is_active=True)

    for offer in offers:
        try:
            brand, model = offer.car_model.split()[:2]
            matching_cars = Car.objects.filter(
                brand__iexact=brand,
                model__iexact=model,
                price__lte=offer.max_price,
                is_active=True,
            )

            if matching_cars.exists():
                best_car = matching_cars.order_by("price").first()
                Deal.objects.create(
                    car=best_car,
                    dealer=best_car.dealer,
                    customer=offer.customer,
                    price=best_car.price,
                )
                offer.status = "accepted"
                logger.info(f"Accepted offer {offer.id} for {best_car}")
            else:
                offer.status = "rejected"

            offer.save()

        except Exception as e:
            logger.error(f"Error processing offer {offer.id}: {e}")


@shared_task
def generate_daily_reports():
    """Генерация ежедневных отчетов"""
    from datetime import datetime, timedelta

    from autodealer_backend.dealers.models import Dealer

    report_date = datetime.now() - timedelta(days=1)

    for dealer in Dealer.objects.filter(is_active=True):
        deals = Deal.objects.filter(dealer=dealer, created_at__date=report_date.date())

        report_data = {
            "dealer": dealer.name,
            "date": report_date.date(),
            "total_sales": deals.count(),
            "total_revenue": sum(d.price for d in deals),
            "top_models": list(
                deals.values("car__model")
                .annotate(count=Count("id"))
                .order_by("-count")[:3]
            ),
        }

        logger.info(f"Daily report for {dealer.name}: {report_data}")
        # Здесь можно добавить отправку отчета на email
