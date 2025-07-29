from decimal import Decimal

from rest_framework import serializers

from .models import Deal, Offer


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = "__all__"

    def validate_max_price(self, value):
        if value < Decimal("0"):
            raise serializers.ValidationError("Price cannot be negative")
        return value

    def validate_status(self, value):
        if value not in dict(Offer.STATUS_CHOICES).keys():
            raise serializers.ValidationError("Invalid status")
        return value


class DealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deal
        fields = "__all__"

    def validate_price(self, value):
        if value < Decimal("0"):
            raise serializers.ValidationError("Price cannot be negative")
        return value
