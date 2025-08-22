from datetime import timedelta

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "purchase-cars-from-suppliers": {
        "task": "dealers.tasks.purchase_cars_from_suppliers",
        "schedule": timedelta(minutes=1),
    },
    "check-best-suppliers": {
        "task": "suppliers.tasks.check_and_update_best_suppliers",
        "schedule": crontab(minute=0),
    },
    "process-customer-offers": {
        "task": "deals.tasks.process_pending_offers",
        "schedule": timedelta(minutes=1),
    },
}
