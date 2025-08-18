from autodealer_backend.cars.celery_tasks.purchase_strategy import PurchaseStrategy
from autodealer_backend.dealers.models import Dealer


class CarTasksFacade:
    @staticmethod
    def purchase_cars():
        dealers = Dealer.objects.filter(is_active=True)
        total = 0

        for dealer in dealers:
            strategy = PurchaseStrategy(dealer)
            if car := strategy.purchase():
                total += 1

        return f"Purchased {total} cars"
