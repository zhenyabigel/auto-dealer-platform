from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from autodealer_backend.deals.filters import OfferFilter
from autodealer_backend.deals.models.offer_model import Offer
from autodealer_backend.deals.serializers import OfferSerializer


class OfferViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = (
        Offer.objects.select_related("customer", "car_model")
        .prefetch_related("preferred_dealers")
        .all()
    )
    serializer_class = OfferSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = OfferFilter
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Offer.objects.none()

        qs = super().get_queryset()
        user = self.request.user

        if not user.is_authenticated:
            return qs.none()

        if not user.is_staff:
            qs = qs.filter(customer=user)

        return qs

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "car_brand",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Filter by car brand",
            ),
            openapi.Parameter(
                "active",
                openapi.IN_QUERY,
                type=openapi.TYPE_BOOLEAN,
                description="Only active offers",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        self.get_object()
        # TODO логика принятия сделки
        return Response({"status": "offer accepted"})
