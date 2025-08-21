import django_filters
from django.utils import timezone

from autodealer_backend.promotion.models.promotion_model import Promotion


class PromotionFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains", label="Название акции")
    current = django_filters.BooleanFilter(
        method="filter_current", label="Текущие акции"
    )
    dealer_name = django_filters.CharFilter(
        field_name="dealer__name", lookup_expr="icontains", label="Дилер"
    )
    discount_percent__gt = django_filters.NumberFilter(
        field_name="discount_percent", lookup_expr="gt", label="Скидка от (%)"
    )
    car_brand = django_filters.CharFilter(
        field_name="promotion_cars__car_model__brand",
        lookup_expr="icontains",
        label="Бренд автомобиля",
    )

    class Meta:
        model = Promotion
        fields = ["promotion_type", "is_active"]

    def filter_current(self, queryset, name, value):
        if value:
            now = timezone.now()
            return queryset.filter(
                start_date__lte=now, end_date__gte=now, is_active=True
            )
        return queryset
