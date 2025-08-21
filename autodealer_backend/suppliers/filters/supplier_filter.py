import django_filters

from autodealer_backend.suppliers.models import Supplier


class SupplierFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    country = django_filters.CharFilter(
        field_name="country__name", lookup_expr="icontains"
    )
    year_established__gt = django_filters.NumberFilter(
        field_name="year_established", lookup_expr="gt"
    )
    year_established__lt = django_filters.NumberFilter(
        field_name="year_established", lookup_expr="lt"
    )
    has_active_offers = django_filters.BooleanFilter(method="filter_has_active_offers")
    supplier_type = django_filters.MultipleChoiceFilter(choices=Supplier.SUPPLIER_TYPES)

    class Meta:
        model = Supplier
        fields = {
            "discount_for_dealers": ["gt", "lt"],
            "average_delivery_time": ["lte"],
            "is_active": ["exact"],
        }

    def filter_has_active_offers(self, queryset, name, value):
        if value:
            return queryset.filter(offers__is_active=True).distinct()
        return queryset
