from .models import Tenant


class TenantMiddleware:
    """Attach the current tenant from X-Tenant-ID for early API isolation work."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.tenant = None
        tenant_id = request.headers.get("X-Tenant-ID")
        if tenant_id:
            request.tenant = Tenant.objects.filter(id=tenant_id, is_active=True).first()
        return self.get_response(request)
