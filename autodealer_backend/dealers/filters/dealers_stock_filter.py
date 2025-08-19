import django_filters

from autodealer_backend.dealers.models import DealerStock


class DealerStockFilter(django_filters.FilterSet):
    dealer = django_filters.CharFilter(
        field_name="dealer__name", lookup_expr="icontains"
    )
    car_brand = django_filters.CharFilter(
        field_name="car_model__brand", lookup_expr="icontains"
    )
    car_model = django_filters.CharFilter(
        field_name="car_model__model", lookup_expr="icontains"
    )
    price__gt = django_filters.NumberFilter(
        field_name="selling_price", lookup_expr="gt"
    )
    price__lt = django_filters.NumberFilter(
        field_name="selling_price", lookup_expr="lt"
    )
    arrival_date__gte = django_filters.DateFilter(
        field_name="arrival_date", lookup_expr="gte"
    )
    has_vin = django_filters.BooleanFilter(
        field_name="vin", lookup_expr="isnull", exclude=True
    )
    is_available = django_filters.BooleanFilter(
        method="filter_available", label="Only available cars"
    )

    class Meta:
        model = DealerStock
        fields = {
            "condition": ["exact"],
            "color": ["exact", "icontains"],
            "is_sold": ["exact"],
            "is_active": ["exact"],
        }

    def filter_available(self, queryset, name, value):
        if value:
            return queryset.filter(is_sold=False, is_active=True)
        return queryset
