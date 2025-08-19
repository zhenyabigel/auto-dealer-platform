import django_filters

from autodealer_backend.promotion.models.promotion_car_model import PromotionCar


class PromotionCarFilter(django_filters.FilterSet):
    promotion = django_filters.NumberFilter(
        field_name="promotion__id", help_text="ID акции"
    )
    promotion_name = django_filters.CharFilter(
        field_name="promotion__name",
        lookup_expr="icontains",
        help_text="Название акции",
    )
    car_brand = django_filters.CharFilter(
        field_name="car_model__brand",
        lookup_expr="icontains",
        help_text="Бренд автомобиля",
    )
    car_model = django_filters.CharFilter(
        field_name="car_model__model",
        lookup_expr="icontains",
        help_text="Модель автомобиля",
    )
    special_price__gt = django_filters.NumberFilter(
        field_name="special_price", lookup_expr="gt", help_text="Спец цена от"
    )
    special_price__lt = django_filters.NumberFilter(
        field_name="special_price", lookup_expr="lt", help_text="Спец цена до"
    )
    has_special_price = django_filters.BooleanFilter(
        method="filter_has_special_price", help_text="Есть специальная цена"
    )
    active_promotion = django_filters.BooleanFilter(
        method="filter_active_promotion", help_text="Только активные акции"
    )

    class Meta:
        model = PromotionCar
        fields = []

    def filter_has_special_price(self, queryset, name, value):
        if value:
            return queryset.filter(special_price__isnull=False)
        return queryset.filter(special_price__isnull=True)

    def filter_active_promotion(self, queryset, name, value):
        from django.utils import timezone

        if value:
            now = timezone.now()
            return queryset.filter(
                promotion__is_active=True,
                promotion__start_date__lte=now,
                promotion__end_date__gte=now,
            )
        return queryset
