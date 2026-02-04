from django.core.validators import MinValueValidator
from django.db import models
from django_countries.fields import CountryField

from autodealer_backend.users.models import User


class Dealer(models.Model):
    DEALER_TYPES = (
        ("premium", "Премиальный"),
        ("standard", "Стандартный"),
        ("discount", "Дискаунтер"),
    )

    user: models.OneToOneField = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="dealer_profile",
        limit_choices_to={"role": "dealer"},
    )
    name: models.CharField = models.CharField(max_length=100, unique=True)
    legal_name: models.CharField = models.CharField(
        blank=True, null=True, max_length=200
    )
    dealer_type: models.CharField = models.CharField(
        max_length=20, choices=DEALER_TYPES, default="standard"
    )
    location: CountryField = CountryField()
    address: models.TextField = models.TextField(
        blank=True, null=True, verbose_name="Адрес"
    )
    phone: models.CharField = models.CharField(max_length=20)
    email: models.EmailField = models.EmailField(
        blank=True, null=True, verbose_name="Почта"
    )
    website = models.URLField(blank=True)
    contact_person: models.CharField = models.CharField(
        blank=True, null=True, verbose_name="Контактное лицо", max_length=100
    )
    balance: models.DecimalField = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Баланс в USD",
    )
    is_active: models.BooleanField = models.BooleanField(default=True)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)
    preferred_car_models: models.ManyToManyField = models.ManyToManyField(
        "cars.CarModel",
        blank=True,
        related_name="preferred_by_dealers",
        help_text="Предпочитаемые модели автомобилей",
    )

    class Meta:
        ordering = ["name"]
        app_label = "dealers"
        verbose_name = "Автосалон"
        verbose_name_plural = "Автосалоны"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["location", "is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.location})"

    @property
    def stock_count(self):
        return self.dealer_stock.filter(is_sold=False).count()

    @property
    def total_stock_value(self):
        from django.db.models import Sum

        result = self.dealer_stock.filter(is_sold=False).aggregate(
            total=Sum("selling_price")
        )
        return result["total"] or 0
