from django.test import RequestFactory, TestCase

from .middleware import TenantMiddleware
from .models import Branch, Tenant


class TenantModelTests(TestCase):
    def test_branch_code_is_unique_per_tenant(self):
        tenant = Tenant.objects.create(name="Ubuntu Funerals", slug="ubuntu-funerals")

        Branch.objects.create(tenant=tenant, name="Soweto", code="SWT")

        self.assertEqual(tenant.branches.count(), 1)


class TenantMiddlewareTests(TestCase):
    def test_attaches_tenant_from_header(self):
        tenant = Tenant.objects.create(name="RestWell Demo", slug="restwell-demo")
        request = RequestFactory().get("/", HTTP_X_TENANT_ID=str(tenant.id))

        TenantMiddleware(lambda req: req)(request)

        self.assertEqual(request.tenant, tenant)
