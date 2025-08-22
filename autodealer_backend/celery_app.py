# autodealer_backend/celery_app.py
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("autodealer_backend")

# Загружаем настройки из Django
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматически находит задачи в приложениях
app.autodiscover_tasks()


# Подключаем периодические задачи после настройки
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    from .celery_beat import CELERY_BEAT_SCHEDULE

    for task_name, task_config in CELERY_BEAT_SCHEDULE.items():
        sender.add_periodic_task(
            task_config["schedule"],
            sender.signature(task_config["task"]),
            name=task_name,
        )
