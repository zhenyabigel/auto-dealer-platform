from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Очищает всю базу данных кроме суперпользователей"

    def handle(self, *args, **options):
        models = [
            "cars.CarModel",
            "cars.CarFeature",
            "suppliers.Supplier",
            "suppliers.SupplierOffer",
            "dealers.Dealer",
            "dealers.DealerStock",
            "deals.Offer",
            "deals.Deal",
            "promotion.Promotion",
            "promotion.PromotionCar",
        ]

        User = get_user_model()

        for model in models:
            try:
                app_label, model_name = model.split(".")
                model_class = apps.get_model(app_label, model_name)
                model_class.objects.all().delete()
                self.stdout.write(f"Очищена модель {model}")
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"Ошибка при очистке {model}: {e}")
                )

        User.objects.filter(is_superuser=False).delete()
        self.stdout.write("Очищены все пользователи кроме админов")

        self.stdout.write(self.style.SUCCESS("База данных очищена!"))
