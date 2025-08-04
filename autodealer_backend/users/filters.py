import django_filters
from django_filters import DateFromToRangeFilter

from .models import Customer, User


class UserFilter(django_filters.FilterSet):
    created_at_range = DateFromToRangeFilter(field_name="date_joined")

    class Meta:
        model = User
        fields = {
            "email": ["icontains"],
            "is_verified": ["exact"],
            "is_active": ["exact"],
        }


class CustomerFilter(django_filters.FilterSet):
    balance__gt = django_filters.NumberFilter(field_name="balance", lookup_expr="gt")
    created_at_range = DateFromToRangeFilter(field_name="created_at")

    class Meta:
        model = Customer
        fields = {
            "country": ["exact"],
            "is_active": ["exact"],
            "user__email": ["icontains"],
        }
