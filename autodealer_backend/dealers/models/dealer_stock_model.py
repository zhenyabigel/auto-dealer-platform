from django.db import models

from autodealer_backend.cars.models import CarModel
from autodealer_backend.dealers.models import Dealer
from autodealer_backend.suppliers.models import Supplier


class DealerStock(models.Model):
    CONDITION_CHOICES = (
        ("new", "Новый"),
        ("used", "Б/у"),
        ("demo", "Демо"),
    )

    dealer = models.ForeignKey(
        Dealer, on_delete=models.CASCADE, related_name="dealer_stock"
    )
    car_model = models.ForeignKey(
        CarModel, on_delete=models.CASCADE, related_name="dealer_inventory"
    )
    supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True, blank=True
    )
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    vin = models.CharField(max_length=17, unique=True, blank=True)
    mileage = models.PositiveIntegerField(default=0)
    color = models.CharField(max_length=30)
    condition = models.CharField(max_length=4, choices=CONDITION_CHOICES, default="new")
    is_sold = models.BooleanField(default=False)
    arrival_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-arrival_date"]
        app_label = "dealers"
        verbose_name = "Автомобиль в наличии"
        verbose_name_plural = "Автомобили в наличии"

    def __str__(self):
        return f"{self.car_model} ({self.condition}) - {self.dealer.name}"

    @property
    def profit(self):
        return self.selling_price - self.purchase_price if self.is_sold else 0

    @property
    def days_in_stock(self):
        from django.utils.timezone import now

        return (now().date() - self.arrival_date).days if not self.is_sold else 0
