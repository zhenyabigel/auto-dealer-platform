from django.db import models

from autodealer_backend.dealers.models import Dealer


class Promotion(models.Model):
    PROMOTION_TYPES = [
        ("supplier", "От поставщика"),
        ("dealer", "От дилера"),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    promotion_type = models.CharField(max_length=10, choices=PROMOTION_TYPES)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    discount_percent = models.PositiveIntegerField()
    max_discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    dealer = models.ForeignKey(
        Dealer,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="promotions",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "promotion"
        ordering = ["-start_date"]
        verbose_name = "Акция"
        verbose_name_plural = "Акции"

    def __str__(self):
        return self.name
