from django.test import RequestFactory, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
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


class TenantApiTests(APITestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="RestWell Demo", slug="restwell-demo")
        self.other_tenant = Tenant.objects.create(name="Other Care", slug="other-care")
        self.branch = Branch.objects.create(tenant=self.tenant, name="Johannesburg", code="JHB")
        self.other_branch = Branch.objects.create(tenant=self.other_tenant, name="Cape Town", code="CPT")
        self.super_admin = User.objects.create_user(
            username="platform",
            password="test-password",
            role=User.Role.SUPER_ADMIN,
            is_staff=True,
        )
        self.tenant_admin = User.objects.create_user(
            username="tenant-admin",
            password="test-password",
            tenant=self.tenant,
            branch=self.branch,
            role=User.Role.TENANT_ADMIN,
        )

    def authenticate(self, username):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": username, "password": "test-password"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_super_admin_can_manage_tenants(self):
        self.authenticate("platform")

        response = self.client.post(
            reverse("tenant-list"),
            {"name": "Ubuntu Funerals", "slug": "ubuntu-funerals"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_tenant_admin_cannot_manage_tenants(self):
        self.authenticate("tenant-admin")

        response = self.client.get(reverse("tenant-list"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_tenant_admin_only_sees_own_branches(self):
        self.authenticate("tenant-admin")

        response = self.client.get(reverse("branch-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        branch_ids = {branch["id"] for branch in response.data}
        self.assertEqual(branch_ids, {self.branch.id})
        self.assertNotIn(self.other_branch.id, branch_ids)

    def test_tenant_admin_cannot_create_branch_for_another_tenant(self):
        self.authenticate("tenant-admin")

        response = self.client.post(
            reverse("branch-list"),
            {"tenant": self.other_tenant.id, "name": "Blocked", "code": "BLK"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
