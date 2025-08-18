from autodealer_backend.cars.celery_tasks.base_task import BaseTask
from autodealer_backend.cars.celery_tasks.facade import CarTasksFacade


class PurchaseTask(BaseTask):
    @property
    def task_name(self):
        return "cars.celery_tasks.purchase_cars"

    def execute(self):
        return CarTasksFacade.purchase_cars()


purchase_cars_from_suppliers = PurchaseTask().create_task()
