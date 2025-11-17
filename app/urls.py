import os
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),

    # App
    path("api/", include("pagamentos.urls")),

    # JWT
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

if os.getenv("ENABLE_SWAGGER", "False").lower() in {"1", "true", "yes", "on"}:
    try:
        from drf_yasg.views import get_schema_view
        from drf_yasg import openapi
        from rest_framework.permissions import AllowAny

        schema_view = get_schema_view(
            openapi.Info(
                title="Pagamentos API",
                default_version="v1",
                description="API Django + Stripe + Webhooks",
            ),
            public=True,
            permission_classes=[AllowAny],
        )

        urlpatterns += [
            path("docs/", schema_view.with_ui("swagger", cache_timeout=0), name="swagger-ui"),
            path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="redoc"),
            path("swagger.json", schema_view.without_ui(cache_timeout=0), name="swagger-json"),
        ]
    except Exception:
        pass

