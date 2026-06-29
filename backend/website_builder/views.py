from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts.permissions import IsTenantAdminOrPlatformAdmin
from branding.models import TenantBranding
from tenants.models import Tenant
from .models import WebsitePage, WebsiteSite
from .serializers import WebsitePageSerializer, WebsiteSiteSerializer


class TenantScopedWebsiteViewSet(ModelViewSet):
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


class WebsiteSiteViewSet(TenantScopedWebsiteViewSet):
    queryset = WebsiteSite.objects.select_related("tenant")
    serializer_class = WebsiteSiteSerializer

    def perform_create(self, serializer):
        tenant = self.current_tenant()
        if WebsiteSite.objects.filter(tenant=tenant).exists():
            raise ValidationError({"tenant": "A website site already exists for this tenant."})
        serializer.save(tenant=tenant)

    def perform_update(self, serializer):
        serializer.save(tenant=serializer.instance.tenant)


class WebsitePageViewSet(TenantScopedWebsiteViewSet):
    queryset = WebsitePage.objects.select_related("tenant", "site")
    serializer_class = WebsitePageSerializer

    def perform_create(self, serializer):
        tenant = self.current_tenant()
        site = serializer.validated_data["site"]
        if site.tenant_id != tenant.id:
            raise ValidationError({"site": "Website site must belong to the current tenant."})
        serializer.save(tenant=tenant)

    def perform_update(self, serializer):
        site = serializer.validated_data.get("site", serializer.instance.site)
        if site.tenant_id != serializer.instance.tenant_id:
            raise ValidationError({"site": "Website site must belong to this page tenant."})
        serializer.save(tenant=serializer.instance.tenant)


@api_view(["GET"])
@permission_classes([AllowAny])
def public_page(request, tenant_slug, page_slug):
    tenant = get_object_or_404(Tenant, slug=tenant_slug, is_active=True)
    site = get_object_or_404(WebsiteSite, tenant=tenant, is_published=True)
    page = get_object_or_404(WebsitePage, tenant=tenant, site=site, slug=page_slug, is_published=True)
    branding = TenantBranding.objects.filter(tenant=tenant, is_active=True).first()

    return Response(
        {
            "tenant": tenant.slug,
            "site": site.name,
            "slug": page.slug,
            "title": page.title,
            "page_type": page.page_type,
            "content": page.content,
            "branding": {
                "primary_color": branding.primary_color if branding else "#0F766E",
                "secondary_color": branding.secondary_color if branding else "#2563EB",
                "logo": branding.logo.url if branding and branding.logo else "",
                "remove_powered_by": branding.remove_powered_by if branding else False,
            },
        }
    )
