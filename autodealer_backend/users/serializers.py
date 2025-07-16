from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from .models import Customer

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['is_verified'] = user.is_verified
        return token


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Пароль (мин. 8 символов)"
    )
    password2 = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Подтверждение пароля"
    )

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password2', 'phone']
        extra_kwargs = {
            'email': {'help_text': "Email пользователя"},
            'username': {'help_text': "Имя пользователя"},
            'phone': {'help_text': "Номер телефона (необязательно)"},
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords don't match")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'phone', 'is_verified', 'date_joined']
        read_only_fields = ['is_verified', 'date_joined']


class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Customer
        fields = ['id', 'user', 'balance', 'address', 'country', 'is_active', 'created_at']
        read_only_fields = ['is_active', 'created_at']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = UserSerializer(instance.user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()
        return super().update(instance, validated_data)


class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.CharField(
        help_text="Токен подтверждения из email"
    )


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(
        help_text="Email для сброса пароля"
    )


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(
        help_text="Токен для сброса пароля"
    )
    new_password = serializers.CharField(
        style={'input_type': 'password'},
        help_text="Новый пароль"
    )
    new_password2 = serializers.CharField(
        style={'input_type': 'password'},
        help_text="Подтверждение нового пароля"
    )
