import pytest

from autodealer_backend.cars.serializers.car_model_serializer import CarModelSerializer
from autodealer_backend.cars.tests.factories.car_model_factory import CarModelFactory


@pytest.mark.django_db
class TestCarModelSerializer:

    def test_serializer_valid_data(self):
        """Тест валидных данных"""
        data = {
            "brand": "Toyota",
            "model": "Camry",
            "generation": "XV70",
            "production_start": 2017,
            "production_end": 2023,
            "body_types": ["Sedan"],
        }

        serializer = CarModelSerializer(data=data)
        assert serializer.is_valid() is True
        assert serializer.errors == {}

        car_model = serializer.save()
        assert car_model.id is not None
        assert car_model.brand == "Toyota"
        assert car_model.body_types == ["Sedan"]

    def test_serializer_invalid_production_years(self):
        """Тест невалидных годов производства"""
        data = {
            "brand": "Toyota",
            "model": "Camry",
            "generation": "XV70",
            "production_start": 2023,
            "production_end": 2020,  # Конец раньше начала!
            "body_types": ["Sedan"],
        }

        serializer = CarModelSerializer(data=data)
        assert serializer.is_valid() is False
        assert "Год окончания не может быть раньше начала" in str(serializer.errors)

    def test_serializer_empty_body_types(self):
        """Тест пустого body_types"""
        data = {
            "brand": "Toyota",
            "model": "Camry",
            "generation": "XV70",
            "production_start": 2020,
            "body_types": [],  # Пустой список!
        }

        serializer = CarModelSerializer(data=data)
        assert serializer.is_valid() is False
        assert "body_types" in str(serializer.errors)

    def test_serializer_missing_body_types(self):
        """Тест отсутствия body_types"""
        data = {
            "brand": "Toyota",
            "model": "Camry",
            "generation": "XV70",
            "production_start": 2020,
            # Нет body_types!
        }

        serializer = CarModelSerializer(data=data)
        assert serializer.is_valid() is False
        assert "body_types" in str(serializer.errors)

    def test_serializer_update(self):
        """Тест обновления через serializer"""
        car_model = CarModelFactory()
        data = {"model": "Updated Model", "body_types": ["Updated", "Types"]}

        serializer = CarModelSerializer(instance=car_model, data=data, partial=True)
        assert serializer.is_valid() is True
        updated_instance = serializer.save()

        assert updated_instance.model == "Updated Model"
        assert updated_instance.body_types == ["Updated", "Types"]

    def test_serializer_read_only_fields(self):
        """Тест, что read_only поля не обновляются"""
        car_model = CarModelFactory()
        original_created = car_model.created_at

        data = {
            "created_at": "2020-01-01T00:00:00Z",
            "model": "New Model",
            "brand": car_model.brand,
            "generation": car_model.generation,
            "production_start": car_model.production_start,
            "body_types": car_model.body_types,
        }

        serializer = CarModelSerializer(instance=car_model, data=data, partial=True)
        assert serializer.is_valid() is True
        updated_instance = serializer.save()

        assert updated_instance.created_at == original_created
        assert updated_instance.model == "New Model"

    def test_serializer_features_read_only(self):
        """Тест, что features только для чтения"""
        data = {
            "brand": "Toyota",
            "model": "Camry",
            "generation": "XV70",
            "production_start": 2020,
            "body_types": ["Sedan"],
            "features": [{"name": "Test Feature"}],  # Должно игнорироваться
        }

        serializer = CarModelSerializer(data=data)
        assert serializer.is_valid() is True

        car_model = serializer.save()
        assert car_model.id is not None

    def test_serializer_year_validation(self):
        """Тест валидации годов"""
        data = {
            "brand": "Toyota",
            "model": "Camry",
            "generation": "XV70",
            "production_start": 1899,  # Меньше 1900
            "body_types": ["Sedan"],
        }

        serializer = CarModelSerializer(data=data)
        assert serializer.is_valid() is False
        assert "production_start" in serializer.errors
