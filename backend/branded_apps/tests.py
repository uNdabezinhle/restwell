from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from branded_apps.models import AppBuildRequest, TenantAppConfig
from tenants.models import Branch, Tenant


class BrandedAppsApiTests(APITestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="RestWell Demo", slug="restwell-demo")
        self.branch = Branch.objects.create(tenant=self.tenant, name="Johannesburg", code="JHB")
        self.other_tenant = Tenant.objects.create(name="Other Care", slug="other-care")
        self.other_branch = Branch.objects.create(tenant=self.other_tenant, name="Cape Town", code="CPT")
        self.user = User.objects.create_user(
            username="app-admin",
            password="test-password",
            tenant=self.tenant,
            branch=self.branch,
            role=User.Role.TENANT_ADMIN,
        )
        User.objects.create_user(
            username="other-app-admin",
            password="test-password",
            tenant=self.other_tenant,
            branch=self.other_branch,
            role=User.Role.TENANT_ADMIN,
        )

    def authenticate(self, username="app-admin"):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": username, "password": "test-password"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def create_config(self, tenant=None, name="RestWell Demo"):
        tenant = tenant or self.tenant
        return TenantAppConfig.objects.create(
            tenant=tenant,
            app_name=name,
            package_name=f"za.co.restwell.{tenant.slug.replace('-', '_')}",
            primary_color="#123ABC",
            secondary_color="#456DEF",
        )

    def test_creates_app_config_for_current_tenant(self):
        self.authenticate()

        response = self.client.post(
            reverse("tenant-app-config-list"),
            {
                "app_name": "RestWell Demo",
                "package_name": "za.co.restwell.demo",
                "primary_color": "#123ABC",
                "secondary_color": "#456DEF",
                "support_email": "support@example.com",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["tenant"], self.tenant.id)
        self.assertEqual(response.data["primary_color"], "#123ABC")

    def test_rejects_invalid_package_name(self):
        self.authenticate()

        response = self.client.post(
            reverse("tenant-app-config-list"),
            {
                "app_name": "RestWell Demo",
                "package_name": "RestWell Demo",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_request_build_action_queues_android_build(self):
        self.authenticate()
        app_config = self.create_config()

        response = self.client.post(
            reverse("tenant-app-config-request-build", args=[app_config.id]),
            {"git_ref": "feature/sprint-7-branded-app"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], AppBuildRequest.Status.QUEUED)
        self.assertEqual(response.data["tenant"], self.tenant.id)
        self.assertEqual(response.data["requested_by"], self.user.id)

    def test_creates_build_request_for_current_tenant_config(self):
        self.authenticate()
        app_config = self.create_config()

        response = self.client.post(
            reverse("app-build-request-list"),
            {"app_config": app_config.id, "platform": AppBuildRequest.Platform.ANDROID},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["tenant"], self.tenant.id)

    def test_tenant_user_only_sees_own_app_configs(self):
        own_config = self.create_config()
        self.create_config(tenant=self.other_tenant, name="Other Care")
        self.authenticate()

        response = self.client.get(reverse("tenant-app-config-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        config_ids = {config["id"] for config in response.data}
        self.assertEqual(config_ids, {own_config.id})
