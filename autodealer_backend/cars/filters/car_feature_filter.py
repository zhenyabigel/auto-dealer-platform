import django_filters

from autodealer_backend.cars.models import CarFeature


class CarFeatureFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        lookup_expr="icontains", label="Название особенности"
    )
    category = django_filters.MultipleChoiceFilter(
        choices=CarFeature.FEATURE_CATEGORIES, label="Категория"
    )
    car_brand = django_filters.CharFilter(
        field_name="car_model__brand", lookup_expr="icontains", label="Бренд автомобиля"
    )
    car_model_name = django_filters.CharFilter(
        field_name="car_model__model",
        lookup_expr="icontains",
        label="Модель автомобиля",
    )
    is_standard = django_filters.BooleanFilter(label="В базовой комплектации")
    is_optional = django_filters.BooleanFilter(label="Доступно как опция")
    has_description = django_filters.BooleanFilter(
        method="filter_has_description", label="Есть описание"
    )

    class Meta:
        model = CarFeature
        fields = []

    def filter_has_description(self, queryset, name, value):
        if value:
            return queryset.exclude(description="")
        return queryset.filter(description="")
