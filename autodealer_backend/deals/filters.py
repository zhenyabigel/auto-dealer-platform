import django_filters
from django_filters import DateFromToRangeFilter

from .models import Deal, Offer


class OfferFilter(django_filters.FilterSet):
    created_at_range = DateFromToRangeFilter(field_name="created_at")
    max_price__gt = django_filters.NumberFilter(
        field_name="max_price", lookup_expr="gt"
    )

    class Meta:
        model = Offer
        fields = {
            "status": ["exact"],
            "is_active": ["exact"],
            "car_model": ["icontains"],
        }


class DealFilter(django_filters.FilterSet):
    date_range = DateFromToRangeFilter(field_name="date")
    price__gt = django_filters.NumberFilter(field_name="price", lookup_expr="gt")

    class Meta:
        model = Deal
        fields = {
            "dealer__name": ["icontains"],
            "customer__user__email": ["icontains"],
            "is_active": ["exact"],
        }
