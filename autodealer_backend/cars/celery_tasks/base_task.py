import logging
from abc import ABC, abstractmethod

from celery import shared_task

logger = logging.getLogger(__name__)


class BaseTask(ABC):
    def __init__(self):
        self.max_retries = 3
        self.default_retry_delay = 300

    @property
    @abstractmethod
    def task_name(self):
        pass

    def create_task(self):
        task_name = self.task_name

        @shared_task(bind=True, name=task_name, max_retries=self.max_retries)
        def task_impl(task_self, *args, **kwargs):
            try:
                return self.execute(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {task_name}: {e}", exc_info=True)
                raise task_self.retry(exc=e, countdown=self.default_retry_delay)

        return task_impl

    @abstractmethod
    def execute(self, *args, **kwargs):
        pass
