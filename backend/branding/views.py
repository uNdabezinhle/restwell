from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts.permissions import IsTenantAdminOrPlatformAdmin
from tenants.models import Tenant
from .models import TenantBranding
from .serializers import TenantBrandingSerializer


class TenantBrandingViewSet(ModelViewSet):
    queryset = TenantBranding.objects.select_related("tenant")
    serializer_class = TenantBrandingSerializer
    permission_classes = [IsTenantAdminOrPlatformAdmin]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_platform_admin:
            return queryset
        if user.tenant_id:
            return queryset.filter(tenant=user.tenant)
        return queryset.none()

    def current_tenant(self):
        if not self.request.user.tenant_id:
            raise ValidationError("A tenant-scoped user is required.")
        return self.request.user.tenant

    def perform_create(self, serializer):
        tenant = self.current_tenant()
        if TenantBranding.objects.filter(tenant=tenant).exists():
            raise ValidationError({"tenant": "Branding already exists for this tenant."})
        serializer.save(tenant=tenant)

    def perform_update(self, serializer):
        serializer.save(tenant=serializer.instance.tenant)


@api_view(["GET"])
@permission_classes([AllowAny])
def public_theme(request, tenant_slug):
    tenant = get_object_or_404(Tenant, slug=tenant_slug, is_active=True)
    branding = TenantBranding.objects.filter(tenant=tenant, is_active=True).first()
    if not branding:
        return Response(
            {
                "tenant": tenant.slug,
                "primary_color": "#0F766E",
                "secondary_color": "#2563EB",
                "logo": "",
                "remove_powered_by": False,
            }
        )

    serializer = TenantBrandingSerializer(branding, context={"request": request})
    return Response(serializer.data)
