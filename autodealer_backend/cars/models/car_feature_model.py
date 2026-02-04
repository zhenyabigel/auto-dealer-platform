from django.db import models

from autodealer_backend.cars.models.car_model import CarModel


class CarFeature(models.Model):
    FEATURE_CATEGORIES = (
        ("safety", "Безопасность"),
        ("comfort", "Комфорт"),
        ("multimedia", "Мультимедиа"),
        ("exterior", "Экстерьер"),
        ("interior", "Интерьер"),
    )

    car_model: models.ForeignKey = models.ForeignKey(
        CarModel, on_delete=models.CASCADE, related_name="features"
    )
    category: models.CharField = models.CharField(
        max_length=20, choices=FEATURE_CATEGORIES, default="comfort"
    )
    name: models.CharField = models.CharField(max_length=100)
    description: models.TextField = models.TextField(blank=True)
    is_standard: models.BooleanField = models.BooleanField(
        default=False, help_text="Входит в базовую комплектацию"
    )
    is_optional: models.BooleanField = models.BooleanField(
        default=False, help_text="Доступно как опция"
    )

    class Meta:
        unique_together = ("car_model", "name")
        app_label = "cars"
        ordering = ["car_model", "name"]
        verbose_name = "Особенность автомобиля"
        verbose_name_plural = "Особенности автомобилей"

    def __str__(self):
        return f"{self.car_model}: {self.name}"

    def save(self, *args, **kwargs):
        if self.is_standard is not None and self.is_optional is None:
            self.is_optional = not self.is_standard
        super().save(*args, **kwargs)
