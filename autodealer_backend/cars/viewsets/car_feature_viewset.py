from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets

from autodealer_backend.cars.filters import CarFeatureFilter
from autodealer_backend.cars.models import CarFeature
from autodealer_backend.cars.serializers import CarFeatureSerializer


class CarFeatureViewSet(viewsets.ModelViewSet):
    queryset = CarFeature.objects.select_related("car_model")
    serializer_class = CarFeatureSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CarFeatureFilter
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()

        car_model_id = self.request.query_params.get("car_model")
        if car_model_id:
            qs = qs.filter(car_model_id=car_model_id)

        return qs
