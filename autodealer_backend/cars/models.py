from django.core.validators import MaxValueValidator
from django.db import models


class Supplier(models.Model):
    name = models.CharField(max_length=100, unique=True)
    year_established = models.PositiveIntegerField()
    discount_for_dealers = models.PositiveIntegerField(
        default=0, help_text="Скидка для постоянных клиентов (%)"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (с {self.year_established})"


class Car(models.Model):
    ENGINE_TYPES = [
        ("petrol", "Бензин"),
        ("diesel", "Дизель"),
        ("electric", "Электро"),
        ("hybrid", "Гибрид"),
    ]
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField(validators=[MaxValueValidator(2100)])
    engine_type = models.CharField(max_length=20, choices=ENGINE_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    dealer = models.ForeignKey(
        "dealers.Dealer", on_delete=models.CASCADE, related_name="cars"
    )
    supplier = models.ForeignKey(
        "Supplier", on_delete=models.SET_NULL, null=True, related_name="cars"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"


class Promotion(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    discount_percent = models.PositiveIntegerField()
    dealer = models.ForeignKey(
        "dealers.Dealer", on_delete=models.CASCADE, related_name="promotions"
    )
    cars = models.ManyToManyField("Car", related_name="promotions")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (до {self.end_date.date()})"
