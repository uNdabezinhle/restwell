from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet

from accounts.permissions import IsTenantOperationsUser
from .models import CalendarEvent, Resource
from .serializers import CalendarEventSerializer, ResourceSerializer


class TenantScopedSchedulingViewSet(ModelViewSet):
    permission_classes = [IsTenantOperationsUser]
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


class ResourceViewSet(TenantScopedSchedulingViewSet):
    queryset = Resource.objects.select_related("tenant", "branch")
    serializer_class = ResourceSerializer

    def perform_create(self, serializer):
        tenant = self.current_tenant()
        branch = serializer.validated_data["branch"]
        if branch.tenant_id != tenant.id:
            raise ValidationError({"branch": "Branch must belong to the current tenant."})
        serializer.save(tenant=tenant)


class CalendarEventViewSet(TenantScopedSchedulingViewSet):
    queryset = CalendarEvent.objects.select_related("tenant", "branch", "case", "created_by").prefetch_related("resources")
    serializer_class = CalendarEventSerializer

    def perform_create(self, serializer):
        tenant = self.current_tenant()
        branch = serializer.validated_data["branch"]
        case = serializer.validated_data.get("case")
        resources = serializer.validated_data.get("resources", [])
        starts_at = serializer.validated_data["starts_at"]
        ends_at = serializer.validated_data["ends_at"]
        if starts_at >= ends_at:
            raise ValidationError({"ends_at": "Event end must be after start."})
        if branch.tenant_id != tenant.id:
            raise ValidationError({"branch": "Branch must belong to the current tenant."})
        if case and case.tenant_id != tenant.id:
            raise ValidationError({"case": "Case must belong to the current tenant."})
        for resource in resources:
            if resource.tenant_id != tenant.id:
                raise ValidationError({"resources": "All resources must belong to the current tenant."})
            has_conflict = resource.calendar_events.filter(starts_at__lt=ends_at, ends_at__gt=starts_at).exists()
            if has_conflict:
                raise ValidationError({"resources": f"Resource '{resource.name}' is already booked for this time."})
        serializer.save(tenant=tenant, created_by=self.request.user)
