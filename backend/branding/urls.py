from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import TenantBrandingViewSet, public_theme

router = DefaultRouter()
router.register("settings", TenantBrandingViewSet, basename="branding")

urlpatterns = [
    path("public/<slug:tenant_slug>/", public_theme, name="branding-public-theme"),
] + router.urls
