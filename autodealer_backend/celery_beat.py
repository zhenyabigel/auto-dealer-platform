from datetime import timedelta

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # Задача 1: Закупка авто у поставщиков - каждые 10 минут
    "purchase-cars-from-suppliers": {
        "task": "autodealer_backend.dealers.tasks.purchase_cars_from_suppliers",
        "schedule": timedelta(seconds=10),
        "options": {"queue": "periodic_tasks"},
    },
    # Задача 2: Проверка поставщиков - каждый час
    "check-and-update-suppliers": {
        "task": "autodealer_backend.suppliers.tasks.check_and_update_suppliers",
        "schedule": crontab(minute=0),  # Каждый час в 0 минут
        "options": {"queue": "periodic_tasks"},
    },
    # Задача 3: Обработка офферов покупателей - каждые 5 минут
    "process-pending-offers": {
        "task": "autodealer_backend.deals.tasks.process_pending_offers",
        "schedule": timedelta(seconds=10),
        "options": {"queue": "periodic_tasks"},
    },
    # Дополнительная задача: Очистка просроченных офферов - ежедневно в 6:00
    "expire-old-offers": {
        "task": "autodealer_backend.deals.tasks.expire_old_offers",
        "schedule": crontab(hour=6, minute=0),
        "options": {"queue": "maintenance_tasks"},
    },
    # Дополнительная задача: Очистка офферов поставщиков - ежедневно в 5:00
    "cleanup-supplier-offers": {
        "task": "autodealer_backend.suppliers.tasks.cleanup_supplier_offers",
        "schedule": crontab(hour=5, minute=0),
        "options": {"queue": "maintenance_tasks"},
    },
}
