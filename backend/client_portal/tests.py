from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from cases.models import Case, Deceased, FamilyMember
from client_portal.models import ClientSupportRequest
from notifications.models import NotificationMessage
from policies.models import PolicyEnrollment, PolicyTemplate, Underwriter
from tenants.models import Branch, Tenant
from website_builder.models import WebsiteBlock, WebsitePage, WebsiteSite


class ClientPortalApiTests(APITestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="RestWell Demo", slug="restwell-demo")
        self.branch = Branch.objects.create(tenant=self.tenant, name="Johannesburg", code="JHB")
        self.family_user = User.objects.create_user(
            username="family@restwell.local",
            password="test-password",
            email="family@example.com",
            tenant=self.tenant,
            branch=self.branch,
            role=User.Role.FAMILY,
        )
        self.admin_user = User.objects.create_user(
            username="admin@restwell.local",
            password="test-password",
            email="admin@restwell.local",
            tenant=self.tenant,
            branch=self.branch,
            role=User.Role.TENANT_ADMIN,
        )
        self.deceased = Deceased.objects.create(tenant=self.tenant, branch=self.branch, first_name="Thabo", last_name="Mokoena")
        self.case = Case.objects.create(tenant=self.tenant, branch=self.branch, deceased=self.deceased, reference="CASE-001")
        self.family_member = FamilyMember.objects.create(
            tenant=self.tenant,
            case=self.case,
            first_name="Lerato",
            last_name="Mokoena",
            relationship="Daughter",
            email="family@example.com",
        )
        underwriter = Underwriter.objects.create(tenant=self.tenant, name="Ubuntu Underwriters")
        template = PolicyTemplate.objects.create(
            tenant=self.tenant,
            underwriter=underwriter,
            name="Family Cover",
            cover_amount="25000.00",
            premium_amount="150.00",
        )
        PolicyEnrollment.objects.create(
            tenant=self.tenant,
            policy_template=template,
            underwriter=underwriter,
            family_member=self.family_member,
            policy_number="POL-001",
            start_date="2026-07-01",
        )
        self.notification = NotificationMessage.objects.create(
            tenant=self.tenant,
            recipient_user=self.family_user,
            channel=NotificationMessage.Channel.IN_APP,
            subject="Welcome",
            body="Your portal is ready.",
        )
        self.site = WebsiteSite.objects.create(
            tenant=self.tenant,
            name="RestWell Demo",
            subdomain="restwell-demo",
            is_published=True,
        )
        self.page = WebsitePage.objects.create(
            tenant=self.tenant,
            site=self.site,
            slug="service",
            title="Service Information",
            page_type="service",
            is_published=True,
        )
        WebsiteBlock.objects.create(
            tenant=self.tenant,
            page=self.page,
            block_type="text",
            content={"body": "Memorial service details."},
            sort_order=1,
        )

    def authenticate(self, username="family@restwell.local"):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": username, "password": "test-password"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_client_dashboard_returns_family_context(self):
        self.authenticate()

        response = self.client.get(reverse("client-dashboard"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["tenant"]["slug"], self.tenant.slug)
        self.assertEqual(response.data["family_members"][0]["name"], "Lerato Mokoena")
        self.assertEqual(response.data["cases"][0]["reference"], "CASE-001")
        self.assertEqual(response.data["policies"][0]["policy_number"], "POL-001")
        self.assertEqual(response.data["notifications"][0]["subject"], "Welcome")
        self.assertEqual(response.data["support_requests"], [])
        self.assertEqual(response.data["public_pages"][0]["slug"], "service")
        self.assertEqual(response.data["public_pages"][0]["url"], "/api/websites/public/restwell-demo/service/")

    def test_family_user_creates_support_request(self):
        self.authenticate()

        response = self.client.post(
            reverse("client-support-request-list"),
            {"subject": "Need help", "message": "Please call me."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["tenant"], self.tenant.id)
        self.assertEqual(ClientSupportRequest.objects.get().family_member, self.family_member)

    def test_family_user_marks_own_notification_read(self):
        self.authenticate()

        response = self.client.post(reverse("client-notification-mark-read", args=[self.notification.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notification.refresh_from_db()
        self.assertEqual(self.notification.status, NotificationMessage.Status.READ)
        self.assertIsNotNone(self.notification.read_at)

    def test_tenant_admin_resolves_support_request(self):
        support_request = ClientSupportRequest.objects.create(
            tenant=self.tenant,
            family_member=self.family_member,
            created_by=self.family_user,
            subject="Need help",
            message="Please call me.",
        )
        self.authenticate("admin@restwell.local")

        response = self.client.post(reverse("client-support-request-resolve", args=[support_request.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        support_request.refresh_from_db()
        self.assertEqual(support_request.status, ClientSupportRequest.Status.RESOLVED)
