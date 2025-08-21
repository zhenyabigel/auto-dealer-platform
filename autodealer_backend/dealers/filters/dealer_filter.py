import django_filters
from django_countries import countries

from autodealer_backend.dealers.models import Dealer


class DealerFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    location = django_filters.ChoiceFilter(
        choices=countries, field_name="location", lookup_expr="exact"
    )
    balance__gt = django_filters.NumberFilter(
        field_name="balance", lookup_expr="gt", help_text="Минимальный баланс"
    )
    balance__lt = django_filters.NumberFilter(
        field_name="balance", lookup_expr="lt", help_text="Максимальный баланс"
    )
    has_stock = django_filters.BooleanFilter(
        method="filter_has_stock", help_text="Есть автомобили в наличии"
    )
    dealer_type = django_filters.MultipleChoiceFilter(choices=Dealer.DEALER_TYPES)

    class Meta:
        model = Dealer
        fields = {
            "is_active": ["exact"],
        }

    def filter_has_stock(self, queryset, name, value):
        if value is not None:
            return queryset.filter(dealer_stock__is_sold=False).distinct()
        return queryset
