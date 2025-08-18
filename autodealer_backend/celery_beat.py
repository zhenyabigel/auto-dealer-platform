from datetime import timedelta

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "purchase-cars": {
        "task": "cars.celery_tasks.purchase_cars",
        "schedule": timedelta(minutes=1),
    }
    # # 2. Проверка поставщиков на лучшие условия (каждый час в :00)
    # 'check-suppliers-prices': {
    #     'task': 'cars.celery_tasks.check_suppliers_prices',
    #     'schedule': crontab(minute=0),  # Каждый час в 0 минут
    # },
    # # 3. Обработка предложений покупателей (каждые 5 минут)
    # 'process-customer-offers': {
    #     'task': 'deals.celery_tasks.process_pending_offers',
    #     'schedule': timedelta(minutes=5),
    # },
    #
    # # 4. Ежедневная отчетность (в 6:00 UTC)
    # 'generate-daily-reports': {
    #     'task': 'deals.celery_tasks.generate_daily_reports',
    #     'schedule': crontab(hour=6, minute=0),
    # }
}
