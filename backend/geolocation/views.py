from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts.permissions import IsTenantAdminOrPlatformAdmin
from .models import LocationLog, LocationRoute
from .serializers import LocationLogSerializer, LocationRouteSerializer


class TenantScopedGeolocationViewSet(ModelViewSet):
    permission_classes = [IsTenantAdminOrPlatformAdmin]
    tenant_field = "tenant_id"

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_platform_admin:
            return queryset
        if user.tenant_id:
            return queryset.filter(**{self.tenant_field: user.tenant_id})
        return queryset.none()

    def current_tenant(self):
        if not self.request.user.tenant_id:
            raise ValidationError("A tenant-scoped user is required.")
        return self.request.user.tenant


class LocationRouteViewSet(TenantScopedGeolocationViewSet):
    queryset = LocationRoute.objects.select_related("tenant", "branch", "case", "assigned_to").prefetch_related("logs")
    serializer_class = LocationRouteSerializer

    def perform_create(self, serializer):
        tenant = self.current_tenant()
        branch = serializer.validated_data["branch"]
        case = serializer.validated_data.get("case")
        assigned_to = serializer.validated_data.get("assigned_to")
        if branch.tenant_id != tenant.id:
            raise ValidationError({"branch": "Branch must belong to the current tenant."})
        if case and case.tenant_id != tenant.id:
            raise ValidationError({"case": "Case must belong to the current tenant."})
        if assigned_to and assigned_to.tenant_id != tenant.id:
            raise ValidationError({"assigned_to": "Assigned user must belong to the current tenant."})
        serializer.save(tenant=tenant)

    @action(detail=False, methods=["get"], url_path="active")
    def active(self, request):
        queryset = self.filter_queryset(self.get_queryset().filter(status=LocationRoute.Status.ACTIVE))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class LocationLogViewSet(TenantScopedGeolocationViewSet):
    queryset = LocationLog.objects.select_related("tenant", "route", "user", "case")
    serializer_class = LocationLogSerializer

    def perform_create(self, serializer):
        tenant = self.current_tenant()
        route = serializer.validated_data.get("route")
        user = serializer.validated_data["user"]
        case = serializer.validated_data.get("case")
        if route and route.tenant_id != tenant.id:
            raise ValidationError({"route": "Route must belong to the current tenant."})
        if user.tenant_id != tenant.id:
            raise ValidationError({"user": "Tracked user must belong to the current tenant."})
        if case and case.tenant_id != tenant.id:
            raise ValidationError({"case": "Case must belong to the current tenant."})
        if route and case and route.case_id and route.case_id != case.id:
            raise ValidationError({"case": "Location log case must match the route case."})
        serializer.save(tenant=tenant)
