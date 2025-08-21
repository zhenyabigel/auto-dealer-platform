from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

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
    permission_classes=[
        permissions.AllowAny,
    ],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/auth/", include("autodealer_backend.users.urls.auth_urls")
    ),  # ← /api/auth/
    path("api/users/", include("autodealer_backend.users.urls.users_urls")),
    path("api/cars/", include("autodealer_backend.cars.urls.car_model_urls")),
    path("api/cars-feature/", include("autodealer_backend.cars.urls.car_feature_url")),
    path("api/dealers/", include("autodealer_backend.dealers.urls.dealer_urls")),
    path(
        "api/dealer-stock/",
        include("autodealer_backend.dealers.urls.dealer_stock_urls"),
    ),
    path("api/deals/", include("autodealer_backend.deals.urls.deals_urls")),
    path("api/offers/", include("autodealer_backend.deals.urls.offers_urls")),
    path("api/suppliers/", include("autodealer_backend.suppliers.urls.supplier_urls")),
    path(
        "api/supplier-offer/",
        include("autodealer_backend.suppliers.urls.supplier_offer_urls"),
    ),
    path(
        "api/promotions/", include("autodealer_backend.promotion.urls.promotion_urls")
    ),
    path(
        "api/promotion-cars/",
        include("autodealer_backend.promotion.urls.promotion_cars_urls"),
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

if settings.DEBUG:
    urlpatterns = [
        path("__debug__/", include("debug_toolbar.urls")),
    ] + urlpatterns
