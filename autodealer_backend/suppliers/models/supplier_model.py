from django.db import models
from django.utils import timezone
from django_countries.fields import CountryField

from autodealer_backend.users.models import User


class Supplier(models.Model):
    SUPPLIER_TYPES = (
        ("official", "Официальный дистрибьютор"),
        ("parallel", "Параллельный импорт"),
        ("used", "Поставщик б/у авто"),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="supplier_profile",
        limit_choices_to={"role": "supplier"},
    )
    name = models.CharField(max_length=100, unique=True)
    legal_name = models.CharField(max_length=200, blank=True)
    supplier_type = models.CharField(max_length=20, choices=SUPPLIER_TYPES)
    year_established = models.PositiveIntegerField()
    country = CountryField()
    city = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)
    contact_person = models.CharField(max_length=100)
    average_delivery_time = models.PositiveIntegerField(
        default=14, help_text="Средний срок поставки в днях"
    )
    discount_for_dealers = models.PositiveIntegerField(
        default=0, help_text="Базовая скидка для дилеров (%)"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        app_label = "suppliers"
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["country", "is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_supplier_type_display()})"

    @property
    def active_offers_count(self):
        return self.offers.filter(
            is_active=True,
            valid_from__lte=timezone.now().date(),
            valid_to__gte=timezone.now().date(),
        ).count()

    @property
    def total_active_cars(self):
        from django.db.models import Sum

        result = self.offers.filter(
            is_active=True,
            valid_from__lte=timezone.now().date(),
            valid_to__gte=timezone.now().date(),
        ).aggregate(total=Sum("quantity_available"))
        return result["total"] or 0
