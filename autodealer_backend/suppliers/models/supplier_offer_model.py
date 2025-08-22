from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from autodealer_backend.cars.models import CarModel
from autodealer_backend.suppliers.models import Supplier


class SupplierOffer(models.Model):
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name="offers",  # ИСПРАВЛЕНО: было 'suppliers', стало 'offers'
    )
    car_model = models.ForeignKey(
        CarModel,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="supplier_offers",
    )

    # Гибкие поля для случаев, когда нет CarModel
    raw_brand = models.CharField(max_length=50, blank=True)
    raw_model = models.CharField(max_length=50, blank=True)
    raw_specs = models.JSONField(
        default=dict,
        blank=True,
        help_text="Полные характеристики в JSON (если нет CarModel)",
    )

    # Условия предложения
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Цена за единицу в USD",
    )
    quantity_available = models.PositiveIntegerField(
        default=1, help_text="Доступное количество"
    )
    discount_percent = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(100)],
        help_text="Процент скидки (0-100)",
    )
    valid_from = models.DateField(default=timezone.now)
    valid_to = models.DateField(
        default=timezone.now().date() + timezone.timedelta(days=30)
    )

    # Логистика
    delivery_days = models.PositiveIntegerField(
        default=14, validators=[MinValueValidator(1)], help_text="Срок поставки в днях"
    )
    is_new = models.BooleanField(default=True, help_text="Новый (не б/у)")
    warranty_months = models.PositiveIntegerField(
        default=24, help_text="Гарантия в месяцах"
    )

    # Системные поля
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["price"]
        app_label = "suppliers"  # ИСПРАВЛЕНО: было 'supplier_offers', стало 'suppliers'
        indexes = [
            models.Index(fields=["valid_from", "valid_to"]),
            models.Index(fields=["price"]),
            models.Index(fields=["supplier", "is_active"]),
        ]
        verbose_name = "Предложение поставщика"
        verbose_name_plural = "Предложения поставщиков"

    def __str__(self):
        base = f"{self.supplier.name}: {self.get_car_name()} - ${self.price}"
        if self.discount_percent > 0:
            base += f" (-{self.discount_percent}%)"
        return base

    def get_car_name(self):
        if self.car_model:
            return f"{self.car_model.brand} {self.car_model.model}"
        return f"{self.raw_brand} {self.raw_model} (raw)"

    @property
    def is_active_now(self):
        now = timezone.now().date()
        return self.is_active and self.valid_from <= now <= self.valid_to

    def save(self, *args, **kwargs):
        # УБРАТЬ автоматическое создание CarModel - это плохая практика
        # Создание CarModel должно происходить в отдельном процессе
        super().save(*args, **kwargs)
