import django_filters

from autodealer_backend.deals.models.deal_model import Deal


class DealFilter(django_filters.FilterSet):
    deal_type = django_filters.ChoiceFilter(choices=Deal.DEAL_TYPES)
    car_model = django_filters.CharFilter(
        field_name="dealer_stock__car_model__model", lookup_expr="icontains"
    )
    car_brand = django_filters.CharFilter(
        field_name="dealer_stock__car_model__brand", lookup_expr="icontains"
    )
    price__gt = django_filters.NumberFilter(field_name="price", lookup_expr="gt")
    price__lt = django_filters.NumberFilter(field_name="price", lookup_expr="lt")
    date__gte = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    date__lte = django_filters.DateFilter(field_name="date", lookup_expr="lte")
    completed = django_filters.BooleanFilter(field_name="is_completed")

    class Meta:
        model = Deal
        fields = {
            "customer": ["exact"],
            "dealer": ["exact"],
        }
