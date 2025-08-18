import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("autodealer_backend")
app.config_from_object("django.conf:settings", namespace="CELERY")


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    from django.conf import settings

    if not settings.configured:
        return

    from .cars.tasks import purchase_cars_from_suppliers

    app.register_task(purchase_cars_from_suppliers)


app.autodiscover_tasks()
