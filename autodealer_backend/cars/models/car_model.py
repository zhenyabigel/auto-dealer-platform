from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class CarModel(models.Model):
    ENGINE_TYPES = (
        ("petrol", "Бензин"),
        ("diesel", "Дизель"),
        ("electric", "Электрический"),
        ("hybrid", "Гибрид"),
    )

    TRANSMISSION_TYPES = (
        ("manual", "Механическая"),
        ("automatic", "Автоматическая"),
        ("robot", "Роботизированная"),
        ("cvt", "Вариатор"),
    )

    DRIVE_TYPES = (
        ("fwd", "Передний"),
        ("rwd", "Задний"),
        ("awd", "Полный"),
    )

    brand: models.CharField = models.CharField(max_length=50, db_index=True)
    model: models.CharField = models.CharField(max_length=50, db_index=True)
    generation: models.CharField = models.CharField(max_length=50, blank=True)

    production_start: models.PositiveIntegerField = models.PositiveIntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(2100)]
    )
    production_end: models.PositiveIntegerField = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1900), MaxValueValidator(2100)],
    )

    engine_type: models.CharField = models.CharField(
        max_length=20, choices=ENGINE_TYPES, default="petrol"
    )
    engine_volume: models.DecimalField = models.DecimalField(
        max_digits=3, decimal_places=1, default=2.0
    )
    power: models.PositiveIntegerField = models.PositiveIntegerField(default=150)
    transmission: models.CharField = models.CharField(
        max_length=20, choices=TRANSMISSION_TYPES, default="automatic"
    )
    drive_type: models.CharField = models.CharField(
        max_length=20, choices=DRIVE_TYPES, default="fwd"
    )
    fuel_consumption: models.DecimalField = models.DecimalField(
        max_digits=4, decimal_places=1, default=8.5
    )

    length: models.PositiveIntegerField = models.PositiveIntegerField(default=4500)
    width: models.PositiveIntegerField = models.PositiveIntegerField(default=1800)
    height: models.PositiveIntegerField = models.PositiveIntegerField(default=1500)
    weight: models.PositiveIntegerField = models.PositiveIntegerField(default=1500)

    body_types: ArrayField = ArrayField(
        models.CharField(max_length=20),
        default=list,
        help_text="Типы кузова (седан, универсал и т.д.)",
    )
    seats: models.PositiveSmallIntegerField = models.PositiveSmallIntegerField(
        default=5
    )
    doors: models.PositiveSmallIntegerField = models.PositiveSmallIntegerField(
        default=4
    )

    is_active: models.BooleanField = models.BooleanField(default=True)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("brand", "model", "generation")
        ordering = ["brand", "model", "production_start"]
        app_label = "cars"
        verbose_name = "Модель автомобиля"
        verbose_name_plural = "Модели автомобилей"

    def __str__(self):
        return f"{self.brand} {self.model}"
