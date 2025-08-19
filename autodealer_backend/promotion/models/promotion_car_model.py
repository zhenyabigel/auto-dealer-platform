from django.db import models

from autodealer_backend.cars.models.car_model import CarModel
from autodealer_backend.promotion.models.promotion_model import Promotion


class PromotionCar(models.Model):
    promotion = models.ForeignKey(
        Promotion, on_delete=models.CASCADE, related_name="promotion_cars"
    )
    car_model = models.ForeignKey(
        CarModel, on_delete=models.CASCADE, related_name="car_promotions"
    )
    special_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    class Meta:
        app_label = "promotion"
        db_table = "promotion_car_relations"
        unique_together = ("promotion", "car_model")
        verbose_name = "Автомобиль в акции"
        verbose_name_plural = "Автомобили в акциях"
