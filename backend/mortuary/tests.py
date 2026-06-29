from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from cases.models import Case, Deceased
from mortuary.models import MortuaryRecord, PreparationTask
from tenants.models import Branch, Tenant


class MortuaryApiTests(APITestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="RestWell Demo", slug="restwell-demo")
        self.branch = Branch.objects.create(tenant=self.tenant, name="Johannesburg", code="JHB")
        self.other_tenant = Tenant.objects.create(name="Other Care", slug="other-care")
        self.other_branch = Branch.objects.create(tenant=self.other_tenant, name="Cape Town", code="CPT")
        self.user = User.objects.create_user(
            username="mortuary-admin",
            password="test-password",
            tenant=self.tenant,
            branch=self.branch,
            role=User.Role.TENANT_ADMIN,
        )
        self.other_user = User.objects.create_user(
            username="other-mortuary-admin",
            password="test-password",
            tenant=self.other_tenant,
            branch=self.other_branch,
            role=User.Role.TENANT_ADMIN,
        )
        self.deceased = Deceased.objects.create(tenant=self.tenant, branch=self.branch, first_name="Thabo", last_name="Mokoena")
        self.case = Case.objects.create(tenant=self.tenant, branch=self.branch, deceased=self.deceased, reference="CASE-001")
        self.other_deceased = Deceased.objects.create(
            tenant=self.other_tenant,
            branch=self.other_branch,
            first_name="Other",
            last_name="Person",
        )

    def authenticate(self, username="mortuary-admin"):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": username, "password": "test-password"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def create_record(self, tenant=None, branch=None, deceased=None, reference="MOR-001"):
        return MortuaryRecord.objects.create(
            tenant=tenant or self.tenant,
            branch=branch or self.branch,
            deceased=deceased or self.deceased,
            case=self.case if tenant is None else None,
            intake_reference=reference,
            status=MortuaryRecord.Status.IN_STORAGE,
            storage_location="Cold Room A",
            storage_unit="A-01",
            intake_at=timezone.now(),
            created_by=self.user,
        )

    def test_creates_mortuary_intake_for_current_tenant(self):
        self.authenticate()

        response = self.client.post(
            reverse("mortuary-record-list"),
            {
                "branch": self.branch.id,
                "case": self.case.id,
                "deceased": self.deceased.id,
                "intake_reference": "MOR-100",
                "storage_location": "Cold Room A",
                "storage_unit": "A-04",
                "intake_at": timezone.now().isoformat(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["tenant"], self.tenant.id)
        self.assertEqual(response.data["created_by"], self.user.id)

    def test_rejects_cross_tenant_deceased_on_intake(self):
        self.authenticate()

        response = self.client.post(
            reverse("mortuary-record-list"),
            {
                "branch": self.branch.id,
                "deceased": self.other_deceased.id,
                "intake_reference": "MOR-101",
                "intake_at": timezone.now().isoformat(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_creates_preparation_task_for_record(self):
        self.authenticate()
        record = self.create_record()

        response = self.client.post(
            reverse("preparation-task-list"),
            {
                "mortuary_record": record.id,
                "task_type": PreparationTask.TaskType.EMBALMING,
                "status": PreparationTask.Status.IN_PROGRESS,
                "assigned_to": self.user.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["tenant"], self.tenant.id)

    def test_tenant_user_only_sees_own_records(self):
        own_record = self.create_record()
        self.create_record(
            tenant=self.other_tenant,
            branch=self.other_branch,
            deceased=self.other_deceased,
            reference="MOR-OTHER",
        )
        self.authenticate()

        response = self.client.get(reverse("mortuary-record-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        record_ids = {record["id"] for record in response.data}
        self.assertEqual(record_ids, {own_record.id})
