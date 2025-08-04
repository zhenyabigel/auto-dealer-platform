import django_filters

from .models import Dealer


class DealerFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")

    balance__gt = django_filters.NumberFilter(
        field_name="balance", lookup_expr="gt", help_text="Минимальный баланс"
    )
    balance__lt = django_filters.NumberFilter(
        field_name="balance", lookup_expr="lt", help_text="Максимальный баланс"
    )

    class Meta:
        model = Dealer
        fields = {
            "location": ["exact"],
            "is_active": ["exact"],
        }
