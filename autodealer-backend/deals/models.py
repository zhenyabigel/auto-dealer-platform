from django.db import models


class Offer(models.Model):
    STATUS_CHOICES = [
        ("pending", "На рассмотрении"),
        ("accepted", "Принято"),
        ("rejected", "Отклонено"),
    ]
    customer = models.ForeignKey(
        "users.Customer", on_delete=models.CASCADE, related_name="offers"
    )
    car_model = models.CharField(
        max_length=100, help_text="Модель (например, 'Toyota Camry')"
    )
    max_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Максимальная цена, которую готов заплатить",
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Предложение #{self.id} ({self.car_model})"


class Deal(models.Model):
    customer = models.ForeignKey(
        "users.Customer", on_delete=models.CASCADE, related_name="purchase_history"
    )
    dealer = models.ForeignKey(
        "dealers.Dealer", on_delete=models.CASCADE, related_name="sales_history"
    )
    car = models.ForeignKey("cars.Car", on_delete=models.CASCADE, related_name="deals")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Фактическая цена сделки"
    )
    date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Сделка #{self.id} ({self.car.brand} → {self.customer.user.email})"
