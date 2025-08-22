from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets

from autodealer_backend.cars.filters import CarFeatureFilter
from autodealer_backend.cars.models import CarFeature
from autodealer_backend.cars.serializers import CarFeatureSerializer


class CarFeatureViewSet(viewsets.ModelViewSet):
    queryset = CarFeature.objects.select_related("car_model").order_by(
        "car_model", "name"
    )
    serializer_class = CarFeatureSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CarFeatureFilter
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        qs = super().get_queryset()

        car_model_id = self.request.query_params.get("car_model")
        if car_model_id:
            qs = qs.filter(car_model_id=car_model_id)

        return qs

    #
    # def get_queryset(self) -> models.QuerySet[CarFeature]:
    #     """Get queryset with optional car_model filtering."""
    #     qs = super().get_queryset()
    #
    #     # Proper type handling for DRF requests
    #     car_model_id: Optional[str] = self._get_car_model_id_from_request()
    #     if car_model_id:
    #         qs = qs.filter(car_model_id=car_model_id)
    #
    #     return qs
    #
    # def _get_car_model_id_from_request(self) -> Optional[str]:
    #     """Safely extract car_model_id from request with proper type handling."""
    #     if hasattr(self, 'request') and self.request:
    #         # For DRF Request objects
    #         if hasattr(self.request, 'query_params'):
    #             return self.request.query_params.get('car_model')
    #         # For standard Django HttpRequest
    #         elif hasattr(self.request, 'GET'):
    #             return self.request.GET.get('car_model')
    #     return None
