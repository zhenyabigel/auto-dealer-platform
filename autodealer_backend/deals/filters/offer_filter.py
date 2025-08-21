import django_filters
from django.utils import timezone

from autodealer_backend.deals.models.offer_model import Offer


class OfferFilter(django_filters.FilterSet):
    car_model = django_filters.CharFilter(
        field_name="car_model__model",
        lookup_expr="icontains",
        label="Модель автомобиля",
    )
    car_brand = django_filters.CharFilter(
        field_name="car_model__brand", lookup_expr="icontains", label="Бренд автомобиля"
    )
    max_price__gt = django_filters.NumberFilter(
        field_name="max_price", lookup_expr="gt", label="Макс. цена от"
    )
    max_price__lt = django_filters.NumberFilter(
        field_name="max_price", lookup_expr="lt", label="Макс. цена до"
    )
    status = django_filters.MultipleChoiceFilter(
        choices=Offer.STATUS_CHOICES, label="Статус"
    )
    active = django_filters.BooleanFilter(
        method="filter_active", label="Активные офферы"
    )
    expired = django_filters.BooleanFilter(
        method="filter_expired", label="Просроченные офферы"
    )
    customer_name = django_filters.CharFilter(
        field_name="customer__username", lookup_expr="icontains", label="Имя клиента"
    )

    class Meta:
        model = Offer
        fields = {
            "customer": ["exact"],
            "is_active": ["exact"],
            "created_at": ["gte", "lte"],
        }

    def filter_active(self, queryset, name, value):
        if value:
            return queryset.filter(is_active=True, expiry_date__gte=timezone.now())
        return queryset

    def filter_expired(self, queryset, name, value):
        if value:
            return queryset.filter(expiry_date__lt=timezone.now())
        return queryset
