from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from cases.models import Case, Deceased, FamilyMember
from client_portal.models import ClientSupportRequest
from notifications.models import NotificationMessage
from policies.models import PolicyEnrollment, PolicyTemplate, Underwriter
from tenants.models import Branch, Tenant


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
        NotificationMessage.objects.create(
            tenant=self.tenant,
            recipient_user=self.family_user,
            channel=NotificationMessage.Channel.IN_APP,
            subject="Welcome",
            body="Your portal is ready.",
        )

    def authenticate(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "family@restwell.local", "password": "test-password"},
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
