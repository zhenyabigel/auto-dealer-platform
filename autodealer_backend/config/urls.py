from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from autodealer_backend.cars.views import CarViewSet, PromotionViewSet, SupplierViewSet
from autodealer_backend.config import settings
from autodealer_backend.dealers.views import DealerViewSet
from autodealer_backend.deals.views import DealViewSet, OfferViewSet
from autodealer_backend.users.authentication import (
    CustomTokenObtainPairView,
    LogoutView,
)
from autodealer_backend.users.views import CustomerViewSet, UserViewSet

schema_view = get_schema_view(
    openapi.Info(
        title="AutoDealer API",
        default_version="v1",
        description="API documentation for AutoDealer Platform",
        terms_of_service="https://yourapp.com/terms/",
        contact=openapi.Contact(email="contact@autodealer.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
)

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"customers", CustomerViewSet, basename="customer")
router.register(r"dealers", DealerViewSet, basename="dealer")
router.register(r"cars", CarViewSet, basename="car")
router.register(r"suppliers", SupplierViewSet, basename="supplier")
router.register(r"promotions", PromotionViewSet, basename="promotion")
router.register(r"offers", OfferViewSet, basename="offer")
router.register(r"deals", DealViewSet, basename="deal")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path(
        "api/auth/login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/logout/", LogoutView.as_view(), name="logout"),
    path(
        "swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
