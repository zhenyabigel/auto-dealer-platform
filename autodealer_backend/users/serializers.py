from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from autodealer_backend.users.models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data.update(
            {
                "id": self.user.id,
                "email": self.user.email,
                "role": self.user.role,
                "is_verified": self.user.is_verified,
            }
        )
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    password2 = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "password",
            "password2",
            "phone",
            "role",
            "address",
            "country",
        ]
        extra_kwargs = {"role": {"read_only": True}}

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError("Passwords don't match")
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source="get_role_display", read_only=True)
    country = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "phone",
            "role",
            "role_display",
            "balance",
            "address",
            "country",
            "is_verified",
            "date_joined",
        ]
        read_only_fields = ["is_verified", "date_joined"]

    def get_country(self, obj):
        return obj.country.name if obj.country else None


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "phone", "address", "country"]


class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.CharField()


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(style={"input_type": "password"})
    new_password2 = serializers.CharField(style={"input_type": "password"})
