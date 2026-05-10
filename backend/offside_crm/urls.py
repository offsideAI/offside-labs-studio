"""Top-level URL configuration."""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", include("apps.health.urls")),
    # Auth (M1).
    path("api/auth/", include("dj_rest_auth.urls")),
    path("api/auth/registration/", include("dj_rest_auth.registration.urls")),
    # allauth's email-confirmation views — verification links sent by registration land here.
    path("accounts/", include("allauth.urls")),
    # Workspaces / memberships / invitations (M2).
    path("api/", include("apps.workspaces.urls")),
    # OpenAPI schema + Swagger UI. SCHEMA is publicly servable (SERVE_PERMISSIONS in
    # SPECTACULAR_SETTINGS) so codegen works without auth.
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
