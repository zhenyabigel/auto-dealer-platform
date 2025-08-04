from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.crypto import get_random_string
from django_countries.fields import CountryField


class User(AbstractUser):
    email = models.EmailField(
        "email address",
        unique=True,
        blank=False,
        null=False,
        help_text="Email пользователя (обязательное поле)",
        error_messages={"blank": "Email is required", "null": "Email is required"},
    )
    phone = models.CharField(
        max_length=20, blank=True, help_text="Номер телефона (необязательно)"
    )
    is_verified = models.BooleanField(
        default=False, help_text="Флаг подтверждения email"
    )
    verification_token = models.CharField(
        max_length=64, blank=True, null=True, help_text="Токен для подтверждения email"
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        app_label = "users"
        db_table = "users_user"
        ordering = ["-id"]

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.email:
            raise ValueError("User must have an email address")
        if not self.verification_token and not self.is_verified:
            self.verification_token = get_random_string(64)
        super().save(*args, **kwargs)


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer")
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Баланс в USD",
    )
    address = models.TextField(blank=True)
    country = CountryField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"Покупатель: {self.user.email}"
