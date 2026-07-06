from html import escape

from django.http import HttpResponse
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


@api_view(["GET"])
@permission_classes([AllowAny])
def public_page_html(request, tenant_slug, page_slug):
    tenant = get_object_or_404(Tenant, slug=tenant_slug, is_active=True)
    site = get_object_or_404(WebsiteSite, tenant=tenant, is_published=True)
    page = get_object_or_404(WebsitePage, tenant=tenant, site=site, slug=page_slug, is_published=True)
    branding = TenantBranding.objects.filter(tenant=tenant, is_active=True).first()
    blocks = WebsiteBlock.objects.filter(tenant=tenant, page=page, is_visible=True)
    primary_color = branding.primary_color if branding else "#0F766E"
    secondary_color = branding.secondary_color if branding else "#2563EB"
    remove_powered_by = branding.remove_powered_by if branding else False

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(page.title)} | {escape(site.name)}</title>
  <style>
    :root {{ color-scheme: light; --primary: {escape(primary_color)}; --secondary: {escape(secondary_color)}; }}
    body {{ margin: 0; font-family: Arial, sans-serif; color: #17201d; background: #f7faf8; }}
    header {{ background: var(--primary); color: white; padding: 28px min(8vw, 72px); }}
    main {{ max-width: 980px; margin: 0 auto; padding: 32px 20px 56px; }}
    section {{ background: white; border: 1px solid #d9e5df; border-radius: 8px; padding: 24px; margin-bottom: 18px; }}
    h1, h2 {{ margin: 0 0 12px; }}
    p {{ line-height: 1.55; }}
    .hero {{ border-left: 8px solid var(--secondary); }}
    .cta a {{ display: inline-block; color: white; background: var(--primary); padding: 10px 16px; border-radius: 6px; text-decoration: none; }}
    footer {{ color: #5d6b66; text-align: center; padding: 24px; }}
  </style>
</head>
<body>
  <header>
    <h1>{escape(page.title)}</h1>
    <p>{escape(site.name)}</p>
  </header>
  <main>
    {_render_blocks(blocks)}
  </main>
  {"" if remove_powered_by else "<footer>Powered by RestWell</footer>"}
</body>
</html>"""
    return HttpResponse(html)


def _render_blocks(blocks):
    rendered = [_render_block(block) for block in blocks]
    return "\n".join(rendered) if rendered else "<section><p>This page has no visible content yet.</p></section>"


def _render_block(block):
    content = block.content or {}
    headline = escape(str(content.get("headline") or content.get("title") or block.get_block_type_display()))
    body = escape(str(content.get("body") or content.get("text") or ""))
    link_label = escape(str(content.get("link_label") or content.get("button_label") or "Contact us"))
    link_url = escape(str(content.get("link_url") or content.get("url") or "#"))
    css_class = "hero" if block.block_type == WebsiteBlock.BlockType.HERO else "cta" if block.block_type == WebsiteBlock.BlockType.CTA else ""

    if block.block_type == WebsiteBlock.BlockType.CTA:
        return f'<section class="{css_class}"><h2>{headline}</h2><p>{body}</p><a href="{link_url}">{link_label}</a></section>'
    if block.block_type == WebsiteBlock.BlockType.CONTACT:
        phone = escape(str(content.get("phone") or ""))
        email = escape(str(content.get("email") or ""))
        details = "".join([f"<p>{value}</p>" for value in [phone, email] if value])
        return f'<section><h2>{headline}</h2><p>{body}</p>{details}</section>'
    return f'<section class="{css_class}"><h2>{headline}</h2><p>{body}</p></section>'
