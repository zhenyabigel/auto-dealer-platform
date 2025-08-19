from datetime import datetime

from rest_framework import serializers

from autodealer_backend.suppliers.models import Supplier


class SupplierSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    country = serializers.SerializerMethodField()
    active_offers_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Supplier
        fields = [
            "id",
            "user",
            "name",
            "legal_name",
            "supplier_type",
            "year_established",
            "country",
            "city",
            "address",
            "phone",
            "email",
            "website",
            "contact_person",
            "average_delivery_time",
            "discount_for_dealers",
            "is_active",
            "active_offers_count",
            "total_active_cars",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_country(self, obj):
        return obj.country.name if obj.country else None

    def validate(self, data):
        if (
            "year_established" in data
            and data["year_established"] > datetime.now().year
        ):
            raise serializers.ValidationError(
                "Year established cannot be in the future"
            )
        return data
