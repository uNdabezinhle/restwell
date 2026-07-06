from django.shortcuts import get_object_or_404
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts.permissions import IsTenantAdminOrPlatformAdmin
from branding.models import TenantBranding
from platform_core.models import AuditLog, TenantFeature
from platform_core.permissions import HasTenantFeature
from platform_core.services import write_audit_log
from tenants.models import Tenant
from .models import WebsiteBlock, WebsitePage, WebsiteSite
from .serializers import WebsiteBlockSerializer, WebsitePageSerializer, WebsiteSiteSerializer


class TenantScopedWebsiteViewSet(ModelViewSet):
    permission_classes = [IsTenantAdminOrPlatformAdmin, HasTenantFeature]
    feature_code = TenantFeature.Code.WEBSITE_BUILDER
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
    queryset = WebsitePage.objects.select_related("tenant", "site").prefetch_related("blocks")
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

    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, pk=None):
        page = self.get_object()
        page.is_published = True
        page.save(update_fields=["is_published", "updated_at"])
        write_audit_log(
            action=AuditLog.Action.WORKFLOW,
            resource=page,
            actor=request.user,
            description=f"Website page {page.slug} published.",
        )
        return Response(self.get_serializer(page).data)


class WebsiteBlockViewSet(TenantScopedWebsiteViewSet):
    queryset = WebsiteBlock.objects.select_related("tenant", "page", "page__site")
    serializer_class = WebsiteBlockSerializer

    def perform_create(self, serializer):
        tenant = self.current_tenant()
        page = serializer.validated_data["page"]
        if page.tenant_id != tenant.id:
            raise ValidationError({"page": "Website page must belong to the current tenant."})
        serializer.save(tenant=tenant)


@api_view(["GET"])
@permission_classes([AllowAny])
def public_page(request, tenant_slug, page_slug):
    tenant = get_object_or_404(Tenant, slug=tenant_slug, is_active=True)
    site = get_object_or_404(WebsiteSite, tenant=tenant, is_published=True)
    page = get_object_or_404(WebsitePage, tenant=tenant, site=site, slug=page_slug, is_published=True)
    branding = TenantBranding.objects.filter(tenant=tenant, is_active=True).first()
    blocks = WebsiteBlock.objects.filter(tenant=tenant, page=page, is_visible=True)

    return Response(
        {
            "tenant": tenant.slug,
            "site": site.name,
            "slug": page.slug,
            "title": page.title,
            "page_type": page.page_type,
            "content": page.content,
            "blocks": WebsiteBlockSerializer(blocks, many=True).data,
            "branding": {
                "primary_color": branding.primary_color if branding else "#0F766E",
                "secondary_color": branding.secondary_color if branding else "#2563EB",
                "logo": branding.logo.url if branding and branding.logo else "",
                "remove_powered_by": branding.remove_powered_by if branding else False,
            },
        }
    )
