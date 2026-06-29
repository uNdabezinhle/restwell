from django.contrib import admin
from django.urls import include, path
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


class HealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({"status": "ok", "service": "restwell-api"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", HealthView.as_view(), name="health"),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/tenants/", include("tenants.urls")),
    path("api/accounts/", include("accounts.urls")),
    path("api/cases/", include("cases.urls")),
    path("api/policies/", include("policies.urls")),
    path("api/financials/", include("financials.urls")),
    path("api/inventory/", include("inventory.urls")),
    path("api/scheduling/", include("scheduling.urls")),
    path("api/branding/", include("branding.urls")),
    path("api/websites/", include("website_builder.urls")),
]
