from django.core.validators import MinValueValidator
from django.db import models

from autodealer_backend.dealers.models import DealerStock
from autodealer_backend.deals.models.offer_model import Offer
from autodealer_backend.suppliers.models import SupplierOffer
from autodealer_backend.users.models import User


class Deal(models.Model):
    DEAL_TYPES = [
        ("purchase", "Покупка у поставщика"),
        ("sale", "Продажа клиенту"),
    ]

    deal_type: models.CharField = models.CharField(max_length=10, choices=DEAL_TYPES)
    offer: models.ForeignKey = models.ForeignKey(
        Offer, on_delete=models.SET_NULL, null=True, blank=True, related_name="deals"
    )
    dealer_stock: models.ForeignKey = models.ForeignKey(
        DealerStock,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sales",
    )
    customer: models.ForeignKey = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"role": "customer"},
        related_name="purchases",
    )

    dealer: models.ForeignKey = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={"role": "dealer"},
        related_name="supplier_purchases",
    )
    supplier_offer: models.ForeignKey = models.ForeignKey(
        SupplierOffer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deals",
    )

    price: models.DecimalField = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)]
    )
    quantity: models.PositiveIntegerField = models.PositiveIntegerField(default=1)
    date: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    is_completed: models.BooleanField = models.BooleanField(default=False)
    notes: models.TextField = models.TextField(blank=True)

    class Meta:
        ordering = ["-date"]
        app_label = "deals"
        verbose_name = "Сделка"
        verbose_name_plural = "Сделки"
        indexes = [
            models.Index(fields=["deal_type", "date"]),
            models.Index(fields=["customer", "is_completed"]),
        ]

    def __str__(self):
        return f"Сделка #{self.id} ({self.get_deal_type_display()})"

    def save(self, *args, **kwargs):
        if self.deal_type == "sale" and not self.customer and self.offer:
            self.customer = self.offer.customer
        super().save(*args, **kwargs)
