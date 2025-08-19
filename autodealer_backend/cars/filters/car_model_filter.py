import django_filters

from autodealer_backend.cars.models import CarModel


class CarModelFilter(django_filters.FilterSet):
    brand = django_filters.CharFilter(lookup_expr="icontains", label="Бренд")
    model = django_filters.CharFilter(lookup_expr="icontains", label="Модель")
    production_start__gt = django_filters.NumberFilter(
        field_name="production_start", lookup_expr="gt", label="Год выпуска от"
    )
    production_start__lt = django_filters.NumberFilter(
        field_name="production_start", lookup_expr="lt", label="Год выпуска до"
    )
    power__gt = django_filters.NumberFilter(
        field_name="power", lookup_expr="gt", label="Мощность от (л.с.)"
    )
    engine_volume__gt = django_filters.NumberFilter(
        field_name="engine_volume", lookup_expr="gt", label="Объем двигателя от (л)"
    )
    has_features = django_filters.CharFilter(
        method="filter_has_features", label="Имеет особенности"
    )

    class Meta:
        model = CarModel
        fields = {
            "engine_type": ["exact"],
            "transmission": ["exact"],
            "drive_type": ["exact"],
            "seats": ["gt", "lt"],
            "is_active": ["exact"],
        }

    def filter_has_features(self, queryset, name, value):
        if value:
            return queryset.filter(features__name__icontains=value)
        return queryset
