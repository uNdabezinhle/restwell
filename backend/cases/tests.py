from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from cases.models import Case, Deceased, FamilyMember
from tenants.models import Branch, Tenant


class CaseManagementApiTests(APITestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="RestWell Demo", slug="restwell-demo")
        self.branch = Branch.objects.create(tenant=self.tenant, name="Johannesburg", code="JHB")
        self.other_tenant = Tenant.objects.create(name="Other Care", slug="other-care")
        self.other_branch = Branch.objects.create(tenant=self.other_tenant, name="Cape Town", code="CPT")
        self.user = User.objects.create_user(
            username="case-admin",
            password="test-password",
            tenant=self.tenant,
            branch=self.branch,
            role=User.Role.TENANT_ADMIN,
        )
        self.other_user = User.objects.create_user(
            username="other-admin",
            password="test-password",
            tenant=self.other_tenant,
            branch=self.other_branch,
            role=User.Role.TENANT_ADMIN,
        )

    def authenticate(self, username="case-admin"):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": username, "password": "test-password"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def create_deceased(self, tenant=None, branch=None, first_name="Thabo", last_name="Mokoena"):
        tenant = tenant or self.tenant
        branch = branch or self.branch
        return Deceased.objects.create(
            tenant=tenant,
            branch=branch,
            first_name=first_name,
            last_name=last_name,
            id_number="8001015009087",
        )

    def create_case(self, tenant=None, branch=None, reference="CASE-001"):
        tenant = tenant or self.tenant
        branch = branch or self.branch
        deceased = self.create_deceased(tenant=tenant, branch=branch)
        return Case.objects.create(tenant=tenant, branch=branch, deceased=deceased, reference=reference)

    def test_creates_deceased_record_for_current_tenant(self):
        self.authenticate()

        response = self.client.post(
            reverse("deceased-list"),
            {
                "branch": self.branch.id,
                "first_name": "Nomsa",
                "last_name": "Dlamini",
                "id_number": "7501010123088",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["tenant"], self.tenant.id)

    def test_creates_case_for_current_tenant(self):
        self.authenticate()
        deceased = self.create_deceased()

        response = self.client.post(
            reverse("case-list"),
            {
                "branch": self.branch.id,
                "deceased": deceased.id,
                "reference": "CASE-100",
                "status": Case.Status.NEW,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["tenant"], self.tenant.id)
        self.assertEqual(response.data["created_by"], self.user.id)

    def test_adds_family_member_to_case(self):
        self.authenticate()
        case = self.create_case()

        response = self.client.post(
            reverse("familymember-list"),
            {
                "case": case.id,
                "first_name": "Lerato",
                "last_name": "Mokoena",
                "relationship": "Daughter",
                "phone": "+27110000000",
                "is_next_of_kin": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(FamilyMember.objects.get(id=response.data["id"]).is_next_of_kin)

    def test_updates_case_status(self):
        self.authenticate()
        case = self.create_case()

        response = self.client.patch(
            reverse("case-detail", args=[case.id]),
            {"status": Case.Status.IN_PROGRESS},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], Case.Status.IN_PROGRESS)

    def test_tenant_user_only_sees_own_cases(self):
        own_case = self.create_case(reference="CASE-OWN")
        other_case = self.create_case(
            tenant=self.other_tenant,
            branch=self.other_branch,
            reference="CASE-OTHER",
        )
        self.authenticate()

        response = self.client.get(reverse("case-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        case_ids = {case["id"] for case in response.data}
        self.assertEqual(case_ids, {own_case.id})
        self.assertNotIn(other_case.id, case_ids)

    def test_rejects_cross_tenant_case_creation(self):
        self.authenticate()
        other_deceased = self.create_deceased(
            tenant=self.other_tenant,
            branch=self.other_branch,
            first_name="Other",
            last_name="Person",
        )

        response = self.client.post(
            reverse("case-list"),
            {
                "branch": self.branch.id,
                "deceased": other_deceased.id,
                "reference": "CASE-BLOCKED",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
