import django_filters
from django.utils import timezone

from autodealer_backend.suppliers.models import SupplierOffer


class SupplierOfferFilter(django_filters.FilterSet):
    brand = django_filters.CharFilter(
        field_name="car_model__brand", lookup_expr="icontains", label="Бренд автомобиля"
    )
    model = django_filters.CharFilter(
        field_name="car_model__model",
        lookup_expr="icontains",
        label="Модель автомобиля",
    )
    raw_brand = django_filters.CharFilter(
        lookup_expr="icontains", label="Бренд (сырой)"
    )
    raw_model = django_filters.CharFilter(
        lookup_expr="icontains", label="Модель (сырая)"
    )
    price__gt = django_filters.NumberFilter(
        field_name="price", lookup_expr="gt", label="Цена от"
    )
    price__lt = django_filters.NumberFilter(
        field_name="price", lookup_expr="lt", label="Цена до"
    )
    valid_now = django_filters.BooleanFilter(
        method="filter_valid_now", label="Только действующие"
    )
    supplier_name = django_filters.CharFilter(
        field_name="supplier__name", lookup_expr="icontains", label="Поставщик"
    )
    is_new = django_filters.BooleanFilter(label="Только новые")
    delivery_days__lte = django_filters.NumberFilter(
        field_name="delivery_days", lookup_expr="lte", label="Срок поставки до (дней)"
    )

    class Meta:
        model = SupplierOffer
        fields = [
            "brand",
            "model",
            "raw_brand",
            "raw_model",
            "price__gt",
            "price__lt",
            "supplier_name",
            "is_new",
            "delivery_days__lte",
            "is_active",
        ]

    def filter_valid_now(self, queryset, name, value):
        if value:
            now = timezone.now().date()
            return queryset.filter(
                valid_from__lte=now, valid_to__gte=now, is_active=True
            )
        return queryset
