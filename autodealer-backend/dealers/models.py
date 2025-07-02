from django.db import models
from django_countries.fields import CountryField


class Dealer(models.Model):
    name = models.CharField(max_length=100, unique=True)
    location = CountryField()
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Баланс в USD"
    )
    preferred_car_brands = models.JSONField(
        default=list,
        help_text="Список предпочитаемых брендов (например, ['Toyota', 'BMW'])"
    )
    preferred_car_characteristics = models.JSONField(
        default=dict,
        help_text="Характеристики для подбора авто (например, {'year__gte': 2020})"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.location})"
