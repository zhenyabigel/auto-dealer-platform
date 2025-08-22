import pytest

from autodealer_backend.cars.models import CarFeature
from autodealer_backend.cars.serializers import CarFeatureSerializer
from autodealer_backend.cars.tests.factories import CarFeatureFactory, CarModelFactory


@pytest.mark.django_db
class TestCarFeatureSerializer:
    def test_serializer_valid_data(self):
        """Проверка валидных данных"""
        car_model = CarModelFactory()
        data = {
            "car_model": car_model.id,
            "category": "comfort",
            "name": "Климат-контроль",
            "description": "Двухзонный климат",
            "is_standard": True,
            "is_optional": False,
        }
        serializer = CarFeatureSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["name"] == "Климат-контроль"

    def test_serializer_create(self):
        """Проверка создания"""
        car_model = CarModelFactory()
        data = {
            "car_model": car_model.id,
            "category": "safety",
            "name": "ABS",
            "is_standard": True,
        }
        serializer = CarFeatureSerializer(data=data)
        assert serializer.is_valid()
        feature = serializer.save()

        assert CarFeature.objects.count() == 1
        assert feature.car_model == car_model
        assert feature.name == "ABS"

    def test_serializer_update(self):
        """Проверка обновления"""
        feature = CarFeatureFactory(name="Старое имя")
        data = {"name": "Новое имя", "description": "Обновлено"}
        serializer = CarFeatureSerializer(feature, data=data, partial=True)
        assert serializer.is_valid()
        updated = serializer.save()

        assert updated.name == "Новое имя"
        assert updated.description == "Обновлено"

    def test_category_validation(self):
        """Проверка валидации категории"""
        car_model = CarModelFactory()
        data = {
            "car_model": car_model.id,
            "category": "invalid_category",  # Невалидно
            "name": "Тест",
        }
        serializer = CarFeatureSerializer(data=data)
        assert not serializer.is_valid()
        assert "category" in serializer.errors

    def test_unique_together_validation(self):
        """Проверка уникальности (car_model, name)"""
        car_model = CarModelFactory()
        CarFeatureFactory(car_model=car_model, name="ABS")

        data = {
            "car_model": car_model.id,
            "name": "ABS",  # Дубликат!
            "category": "safety",
        }
        serializer = CarFeatureSerializer(data=data)

        # Теперь должна быть ошибка валидации
        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors
        # Проверяем английскую версию ошибки
        assert "unique" in str(serializer.errors["non_field_errors"]).lower()
        assert "car_model" in str(serializer.errors["non_field_errors"])
        assert "name" in str(serializer.errors["non_field_errors"])

    def test_serialization_output(self):
        """Проверка вывода"""
        feature = CarFeatureFactory(
            name="ESP",
            category="safety",
            description="Система стабилизации",
            is_standard=True,
            is_optional=False,
        )
        serializer = CarFeatureSerializer(feature)
        data = serializer.data

        assert data["name"] == "ESP"
        assert data["category"] == "safety"
        assert data["description"] == "Система стабилизации"
        assert data["is_standard"] is True
        assert data["is_optional"] is False
        assert data["car_model"] == feature.car_model.id

    def test_is_optional_auto_set(self):
        """Проверка, что is_optional = not is_standard"""
        car_model = CarModelFactory()
        data = {
            "car_model": car_model.id,
            "category": "comfort",
            "name": "Подогрев сидений",
            "is_standard": False,
            # НЕ передаем is_optional - должно установиться автоматически
        }
        serializer = CarFeatureSerializer(data=data)
        assert serializer.is_valid()
        feature = serializer.save()

        assert feature.is_standard is False
        assert feature.is_optional is True  # Должно быть True

    def test_is_optional_explicit_false(self):
        """Проверка явного указания is_optional=False"""
        car_model = CarModelFactory()
        data = {
            "car_model": car_model.id,
            "category": "comfort",
            "name": "Подогрев сидений",
            "is_standard": False,
            "is_optional": False,  # Явно указываем False
        }
        serializer = CarFeatureSerializer(data=data)
        assert serializer.is_valid()
        feature = serializer.save()

        assert feature.is_standard is False
        assert feature.is_optional is False  # Должно остаться False
