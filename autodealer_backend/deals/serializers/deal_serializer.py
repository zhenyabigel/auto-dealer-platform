from rest_framework import serializers

from autodealer_backend.dealers.models import DealerStock
from autodealer_backend.deals.models.deal_model import Deal
from autodealer_backend.deals.models.offer_model import Offer
from autodealer_backend.suppliers.models import SupplierOffer
from autodealer_backend.users.models import User


class DealSerializer(serializers.ModelSerializer):
    deal_type_display = serializers.CharField(
        source="get_deal_type_display", read_only=True
    )
    customer_name = serializers.CharField(source="customer.username", read_only=True)
    dealer_name = serializers.CharField(source="dealer.username", read_only=True)
    dealer_stock_info = serializers.CharField(
        source="dealer_stock.__str__", read_only=True
    )
    offer_info = serializers.CharField(source="offer.__str__", read_only=True)
    supplier_offer_info = serializers.CharField(
        source="supplier_offer.__str__", read_only=True
    )

    # Write-only поля для ID
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="customer"),
        source="customer",
        write_only=True,
        required=False,
    )
    dealer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="dealer"),
        source="dealer",
        write_only=True,
        required=False,
    )
    dealer_stock_id = serializers.PrimaryKeyRelatedField(
        queryset=DealerStock.objects.all(),
        source="dealer_stock",
        write_only=True,
        required=False,
    )
    offer_id = serializers.PrimaryKeyRelatedField(
        queryset=Offer.objects.all(), source="offer", write_only=True, required=False
    )
    supplier_offer_id = serializers.PrimaryKeyRelatedField(
        queryset=SupplierOffer.objects.all(),
        source="supplier_offer",
        write_only=True,
        required=False,
    )

    class Meta:
        model = Deal
        fields = [
            "id",
            "deal_type",
            "deal_type_display",
            "customer",
            "customer_id",
            "customer_name",
            "dealer",
            "dealer_id",
            "dealer_name",
            "dealer_stock",
            "dealer_stock_id",
            "dealer_stock_info",
            "offer",
            "offer_id",
            "offer_info",
            "supplier_offer",
            "supplier_offer_id",
            "supplier_offer_info",
            "price",
            "quantity",
            "date",
            "is_completed",
            "notes",
        ]
        read_only_fields = ["date"]

    def validate(self, data):
        deal_type = data.get("deal_type")

        if deal_type == "sale":
            if not data.get("dealer_stock"):
                raise serializers.ValidationError(
                    "dealer_stock обязателен для сделок продажи"
                )
            if data["dealer_stock"].is_sold:
                raise serializers.ValidationError("Этот автомобиль уже продан")

        elif deal_type == "purchase":
            if not data.get("supplier_offer"):
                raise serializers.ValidationError(
                    "supplier_offer обязателен для сделок покупки"
                )

        return data
