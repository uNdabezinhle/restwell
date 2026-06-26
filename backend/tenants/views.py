from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import ModelViewSet

from accounts.permissions import IsPlatformAdmin, IsTenantAdminOrPlatformAdmin
from .models import Branch, Tenant
from .serializers import BranchSerializer, TenantSerializer


class TenantViewSet(ModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsPlatformAdmin]


class BranchViewSet(ModelViewSet):
    queryset = Branch.objects.select_related("tenant")
    serializer_class = BranchSerializer
    permission_classes = [IsTenantAdminOrPlatformAdmin]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_platform_admin:
            return queryset
        if user.tenant_id:
            return queryset.filter(tenant_id=user.tenant_id)
        return queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        tenant = serializer.validated_data["tenant"]
        if not user.is_platform_admin and tenant.id != user.tenant_id:
            raise PermissionDenied("Cannot create branches outside your tenant.")
        serializer.save()
