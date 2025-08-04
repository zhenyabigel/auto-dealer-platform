import django_filters
from django.utils import timezone

from .models import Supplier, Car, Promotion


class SupplierFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    year_established__gt = django_filters.NumberFilter(
        field_name='year_established',
        lookup_expr='gt'
    )
    year_established__lt = django_filters.NumberFilter(
        field_name='year_established',
        lookup_expr='lt'
    )
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = Supplier
        fields = [
            'name',
            'year_established',
            'discount_for_dealers',
            'is_active'
        ]


class CarFilter(django_filters.FilterSet):
    brand = django_filters.CharFilter(lookup_expr='icontains')
    model = django_filters.CharFilter(lookup_expr='icontains')
    year__gt = django_filters.NumberFilter(field_name='year', lookup_expr='gt')
    year__lt = django_filters.NumberFilter(field_name='year', lookup_expr='lt')
    price__gt = django_filters.NumberFilter(field_name='price', lookup_expr='gt')
    price__lt = django_filters.NumberFilter(field_name='price', lookup_expr='lt')
    dealer = django_filters.CharFilter(field_name='dealer__name', lookup_expr='icontains')
    supplier = django_filters.CharFilter(field_name='supplier__name', lookup_expr='icontains')

    class Meta:
        model = Car
        fields = {
            'engine_type': ['exact'],
            'is_active': ['exact'],
        }


class PromotionFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    current = django_filters.BooleanFilter(
        method='filter_current',
        label='Текущие акции'
    )
    dealer = django_filters.CharFilter(field_name='dealer__name', lookup_expr='icontains')

    class Meta:
        model = Promotion
        fields = [
            'name',
            'discount_percent',
            'is_active'
        ]

    def filter_current(self, queryset, name, value):
        if value:
            return queryset.filter(
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now()
            )
        return queryset
