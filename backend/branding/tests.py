from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from branding.models import TenantBranding
from tenants.models import Branch, Tenant


class BrandingApiTests(APITestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="RestWell Demo", slug="restwell-demo")
        self.branch = Branch.objects.create(tenant=self.tenant, name="Johannesburg", code="JHB")
        self.other_tenant = Tenant.objects.create(name="Other Care", slug="other-care")
        self.other_branch = Branch.objects.create(tenant=self.other_tenant, name="Cape Town", code="CPT")
        self.user = User.objects.create_user(
            username="branding-admin",
            password="test-password",
            tenant=self.tenant,
            branch=self.branch,
            role=User.Role.TENANT_ADMIN,
        )
        User.objects.create_user(
            username="other-branding-admin",
            password="test-password",
            tenant=self.other_tenant,
            branch=self.other_branch,
            role=User.Role.TENANT_ADMIN,
        )

    def authenticate(self, username="branding-admin"):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": username, "password": "test-password"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_creates_branding_for_current_tenant(self):
        self.authenticate()

        response = self.client.post(
            reverse("branding-list"),
            {
                "primary_color": "#123ABC",
                "secondary_color": "#456DEF",
                "email_from_name": "RestWell Demo",
                "sms_sender_name": "RESTWELL",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["tenant"], self.tenant.id)
        self.assertEqual(response.data["primary_color"], "#123ABC")

    def test_rejects_invalid_brand_color(self):
        self.authenticate()

        response = self.client.post(
            reverse("branding-list"),
            {"primary_color": "blue", "secondary_color": "#456DEF"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_tenant_user_only_sees_own_branding(self):
        own_branding = TenantBranding.objects.create(tenant=self.tenant, primary_color="#111111")
        TenantBranding.objects.create(tenant=self.other_tenant, primary_color="#222222")
        self.authenticate()

        response = self.client.get(reverse("branding-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        branding_ids = {branding["id"] for branding in response.data}
        self.assertEqual(branding_ids, {own_branding.id})

    def test_public_theme_returns_active_tenant_branding(self):
        TenantBranding.objects.create(
            tenant=self.tenant,
            primary_color="#123ABC",
            secondary_color="#456DEF",
            remove_powered_by=True,
        )

        response = self.client.get(reverse("branding-public-theme", args=[self.tenant.slug]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["primary_color"], "#123ABC")
        self.assertTrue(response.data["remove_powered_by"])
