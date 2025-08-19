from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from autodealer_backend.cars.models import CarModel
from autodealer_backend.users.models import User


class Offer(models.Model):
    STATUS_CHOICES = [
        ("pending", "На рассмотрении"),
        ("accepted", "Принято"),
        ("rejected", "Отклонено"),
        ("expired", "Просрочено"),
    ]

    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "customer"},
        related_name="offers",
    )
    car_model = models.ForeignKey(
        CarModel, on_delete=models.CASCADE, related_name="offers"
    )
    max_price = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)]
    )
    preferred_dealers = models.ManyToManyField(
        User,
        limit_choices_to={"role": "dealer"},
        blank=True,
        related_name="received_offers",
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    expiry_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        app_label = "deals"
        verbose_name = "Оффер"
        verbose_name_plural = "Офферы"
        indexes = [
            models.Index(fields=["status", "expiry_date"]),
            models.Index(fields=["customer", "is_active"]),
        ]

    def __str__(self):
        return f"Оффер #{self.id} ({self.car_model})"

    def save(self, *args, **kwargs):
        if not self.expiry_date:
            self.expiry_date = timezone.now() + timezone.timedelta(days=7)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return self.expiry_date < timezone.now()
