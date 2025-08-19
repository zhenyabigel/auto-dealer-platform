# users/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.crypto import get_random_string
from django_countries.fields import CountryField


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    ROLE_CHOICES = [
        ("customer", "Покупатель"),
        ("dealer", "Дилер"),
        ("supplier", "Поставщик"),
        ("admin", "Администратор"),
    ]

    email = models.EmailField(
        "email address",
        unique=True,
        blank=False,
        null=False,
        error_messages={"blank": "Email is required", "null": "Email is required"},
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="customer")
    phone = models.CharField(max_length=20, blank=True)
    balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, help_text="Баланс в USD"
    )
    address = models.TextField(blank=True)
    country = CountryField(blank=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=64, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-date_joined"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["role", "is_active"]),
        ]

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"

    def save(self, *args, **kwargs):
        if not self.email:
            raise ValueError("User must have an email address")
        if not self.verification_token and not self.is_verified:
            self.verification_token = get_random_string(64)
        super().save(*args, **kwargs)

    @property
    def is_customer(self):
        return self.role == "customer"

    @property
    def is_dealer(self):
        return self.role == "dealer"

    @property
    def is_supplier(self):
        return self.role == "supplier"
