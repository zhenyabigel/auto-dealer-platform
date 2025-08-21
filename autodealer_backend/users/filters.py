import django_filters
from django_countries import countries

from .models import User


class UserFilter(django_filters.FilterSet):
    email = django_filters.CharFilter(lookup_expr="icontains")
    role = django_filters.ChoiceFilter(choices=User.ROLE_CHOICES)
    country = django_filters.ChoiceFilter(choices=countries)
    balance__gt = django_filters.NumberFilter(field_name="balance", lookup_expr="gt")
    balance__lt = django_filters.NumberFilter(field_name="balance", lookup_expr="lt")
    date_joined__gte = django_filters.DateFilter(
        field_name="date_joined", lookup_expr="gte"
    )
    date_joined__lte = django_filters.DateFilter(
        field_name="date_joined", lookup_expr="lte"
    )

    class Meta:
        model = User
        fields = {
            "is_verified": ["exact"],
            "is_active": ["exact"],
        }
