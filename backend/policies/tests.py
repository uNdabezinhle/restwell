from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from cases.models import Case, Deceased, FamilyMember
from policies.models import PolicyEnrollment, PolicyTemplate, PremiumPayment, Underwriter
from tenants.models import Branch, Tenant


class PolicyManagementApiTests(APITestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="RestWell Demo", slug="restwell-demo")
        self.branch = Branch.objects.create(tenant=self.tenant, name="Johannesburg", code="JHB")
        self.other_tenant = Tenant.objects.create(name="Other Care", slug="other-care")
        self.other_branch = Branch.objects.create(tenant=self.other_tenant, name="Cape Town", code="CPT")
        self.user = User.objects.create_user(
            username="policy-admin",
            password="test-password",
            tenant=self.tenant,
            branch=self.branch,
            role=User.Role.TENANT_ADMIN,
        )
        self.other_user = User.objects.create_user(
            username="other-policy-admin",
            password="test-password",
            tenant=self.other_tenant,
            branch=self.other_branch,
            role=User.Role.TENANT_ADMIN,
        )
        self.deceased = Deceased.objects.create(
            tenant=self.tenant,
            branch=self.branch,
            first_name="Thabo",
            last_name="Mokoena",
        )
        self.case = Case.objects.create(
            tenant=self.tenant,
            branch=self.branch,
            deceased=self.deceased,
            reference="CASE-001",
        )
        self.family_member = FamilyMember.objects.create(
            tenant=self.tenant,
            case=self.case,
            first_name="Lerato",
            last_name="Mokoena",
            relationship="Daughter",
            is_next_of_kin=True,
        )

    def authenticate(self, username="policy-admin"):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": username, "password": "test-password"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def create_underwriter(self, tenant=None, name="Ubuntu Underwriters"):
        return Underwriter.objects.create(tenant=tenant or self.tenant, name=name)

    def create_template(self, underwriter=None, tenant=None):
        underwriter = underwriter or self.create_underwriter(tenant=tenant)
        return PolicyTemplate.objects.create(
            tenant=tenant or self.tenant,
            underwriter=underwriter,
            name="Family Cover",
            cover_amount="25000.00",
            premium_amount="150.00",
        )

    def create_enrollment(self):
        template = self.create_template()
        return PolicyEnrollment.objects.create(
            tenant=self.tenant,
            policy_template=template,
            underwriter=template.underwriter,
            family_member=self.family_member,
            policy_number="POL-001",
            start_date=date(2026, 6, 1),
        )

    def test_creates_underwriter_for_current_tenant(self):
        self.authenticate()

        response = self.client.post(
            reverse("underwriter-list"),
            {"name": "Ubuntu Underwriters", "registration_number": "UW-001"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["tenant"], self.tenant.id)

    def test_creates_policy_template_with_underwriter(self):
        self.authenticate()
        underwriter = self.create_underwriter()

        response = self.client.post(
            reverse("policytemplate-list"),
            {
                "underwriter": underwriter.id,
                "name": "Family Cover",
                "cover_amount": "25000.00",
                "premium_amount": "150.00",
                "billing_frequency": PolicyTemplate.BillingFrequency.MONTHLY,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["tenant"], self.tenant.id)

    def test_enrolls_family_member_and_assigns_underwriter_from_template(self):
        self.authenticate()
        template = self.create_template()

        response = self.client.post(
            reverse("policyenrollment-list"),
            {
                "policy_template": template.id,
                "family_member": self.family_member.id,
                "policy_number": "POL-100",
                "start_date": "2026-06-01",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["underwriter"], template.underwriter.id)
        self.assertEqual(response.data["created_by"], self.user.id)

    def test_records_premium_payment(self):
        self.authenticate()
        enrollment = self.create_enrollment()

        response = self.client.post(
            reverse("premiumpayment-list"),
            {
                "enrollment": enrollment.id,
                "amount": "150.00",
                "due_date": "2026-07-01",
                "status": PremiumPayment.Status.PENDING,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["tenant"], self.tenant.id)

    def test_tenant_user_only_sees_own_policy_templates(self):
        own_template = self.create_template()
        other_underwriter = self.create_underwriter(tenant=self.other_tenant, name="Other Underwriter")
        other_template = self.create_template(tenant=self.other_tenant, underwriter=other_underwriter)
        self.authenticate()

        response = self.client.get(reverse("policytemplate-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        template_ids = {template["id"] for template in response.data}
        self.assertEqual(template_ids, {own_template.id})
        self.assertNotIn(other_template.id, template_ids)

    def test_rejects_cross_tenant_underwriter_on_template(self):
        self.authenticate()
        other_underwriter = self.create_underwriter(tenant=self.other_tenant, name="Other Underwriter")

        response = self.client.post(
            reverse("policytemplate-list"),
            {
                "underwriter": other_underwriter.id,
                "name": "Blocked Cover",
                "cover_amount": "25000.00",
                "premium_amount": "150.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
