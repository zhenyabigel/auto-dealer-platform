from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from autodealer_backend.deals.filters import DealFilter
from autodealer_backend.deals.models.deal_model import Deal
from autodealer_backend.deals.serializers import DealSerializer


class DealViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Deal.objects.select_related(
        "customer", "dealer", "supplier_offer", "dealer_stock", "offer"
    ).all()
    serializer_class = DealSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = DealFilter
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Deal.objects.none()

        qs = super().get_queryset()
        user = self.request.user

        if not user.is_authenticated:
            return qs.none()

        if user.role == "customer":
            qs = qs.filter(customer=user)
        elif user.role == "dealer":
            qs = qs.filter(dealer=user)

        return qs

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "deal_type",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                enum=["purchase", "sale"],
                description="Filter by deal type",
            ),
            openapi.Parameter(
                "completed",
                openapi.IN_QUERY,
                type=openapi.TYPE_BOOLEAN,
                description="Filter by completion status",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        deal = self.get_object()
        deal.is_completed = True
        deal.save()
        return Response({"status": "deal completed"})
