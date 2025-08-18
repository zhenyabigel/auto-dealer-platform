from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Очищает всю базу данных кроме суперпользователей"

    def handle(self, *args, **options):
        models = [
            "cars.Car",
            "cars.Supplier",
            "cars.Promotion",
            "dealers.Dealer",
            "deals.Offer",
            "deals.Deal",
            "users.Customer",
        ]

        User = get_user_model()

        for model in models:
            app_label, model_name = model.split(".")
            model_class = apps.get_model(app_label, model_name)
            model_class.objects.all().delete()
            self.stdout.write(f"Очищена модель {model}")

        User.objects.filter(is_superuser=False).delete()
        self.stdout.write("Очищены все пользователи кроме админов")

        self.stdout.write(self.style.SUCCESS("База данных очищена!"))
