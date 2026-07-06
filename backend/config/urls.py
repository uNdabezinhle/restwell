from django.contrib import admin
from django.conf import settings
from django.db import connection
from django.urls import include, path
from redis import Redis
from redis.exceptions import RedisError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


class LiveHealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({"status": "ok", "service": "restwell-api"})


class ReadyHealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        checks = {"database": "ok"}
        ready = True

        try:
            connection.ensure_connection()
        except Exception:
            checks["database"] = "unavailable"
            ready = False

        if settings.REDIS_URL:
            checks["redis"] = "ok"
            try:
                Redis.from_url(settings.REDIS_URL, socket_connect_timeout=1).ping()
            except RedisError:
                checks["redis"] = "unavailable"
                ready = False

        response_status = status.HTTP_200_OK if ready else status.HTTP_503_SERVICE_UNAVAILABLE
        return Response({"status": "ok" if ready else "degraded", "checks": checks}, status=response_status)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", LiveHealthView.as_view(), name="health"),
    path("api/health/live/", LiveHealthView.as_view(), name="health-live"),
    path("api/health/ready/", ReadyHealthView.as_view(), name="health-ready"),
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
    path("api/mortuary/", include("mortuary.urls")),
    path("api/geolocation/", include("geolocation.urls")),
    path("api/branded-apps/", include("branded_apps.urls")),
    path("api/onboarding/", include("onboarding.urls")),
    path("api/", include("platform_core.urls")),
    path("api/notifications/", include("notifications.urls")),
]
