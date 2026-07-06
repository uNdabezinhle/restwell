from datetime import date
from decimal import Decimal

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from cases.models import Case, Deceased
from financials.models import Invoice, InvoiceLineItem
from inventory.models import InventoryItem
from mortuary.models import MortuaryRecord
from platform_core.models import AuditLog, TenantFeature
from tenants.models import Branch, Tenant


class PlatformCoreApiTests(APITestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="RestWell Demo", slug="restwell-demo")
        self.branch = Branch.objects.create(tenant=self.tenant, name="Johannesburg", code="JHB")
        self.user = User.objects.create_user(
            username="platform-admin",
            password="test-password",
            tenant=self.tenant,
            branch=self.branch,
            role=User.Role.TENANT_ADMIN,
        )
        self.deceased = Deceased.objects.create(tenant=self.tenant, branch=self.branch, first_name="Thabo", last_name="Mokoena")
        self.case = Case.objects.create(tenant=self.tenant, branch=self.branch, deceased=self.deceased, reference="CASE-001", created_by=self.user)

    def authenticate(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "platform-admin", "password": "test-password"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_dashboard_summary_returns_module_counts(self):
        self.authenticate()

        response = self.client.get(reverse("dashboard-summary"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["operations"]["cases"], 1)
        self.assertEqual(response.data["operations"]["deceased"], 1)

    def test_disabled_feature_denies_paid_module(self):
        TenantFeature.objects.create(tenant=self.tenant, code=TenantFeature.Code.MORTUARY, is_enabled=False)
        self.authenticate()

        response = self.client.get(reverse("mortuary-record-list"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_tenant_admin_updates_feature_state(self):
        feature = TenantFeature.objects.create(
            tenant=self.tenant,
            code=TenantFeature.Code.WEBSITE_BUILDER,
            is_enabled=True,
        )
        self.authenticate()

        response = self.client.patch(
            reverse("tenant-feature-detail", args=[feature.id]),
            {"is_enabled": False},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        feature.refresh_from_db()
        self.assertFalse(feature.is_enabled)

    def test_advance_case_status_writes_audit_log(self):
        self.authenticate()

        response = self.client.post(
            reverse("case-advance-status", args=[self.case.id]),
            {"status": Case.Status.COMPLETED},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.case.refresh_from_db()
        self.assertEqual(self.case.status, Case.Status.COMPLETED)
        self.assertTrue(AuditLog.objects.filter(action=AuditLog.Action.WORKFLOW, resource_id=str(self.case.id)).exists())

    def test_invoice_record_payment_workflow(self):
        self.authenticate()
        invoice = Invoice.objects.create(
            tenant=self.tenant,
            branch=self.branch,
            case=self.case,
            invoice_number="INV-001",
            customer_name="Lerato Mokoena",
            issue_date=date.today(),
            due_date=date.today(),
            created_by=self.user,
        )
        InvoiceLineItem.objects.create(
            tenant=self.tenant,
            invoice=invoice,
            description="Service fee",
            quantity=Decimal("1.00"),
            unit_price=Decimal("100.00"),
        )

        response = self.client.post(
            reverse("invoice-record-payment", args=[invoice.id]),
            {"amount": "100.00", "method": "cash"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        invoice.refresh_from_db()
        self.assertEqual(invoice.amount_paid, Decimal("100.00"))
        self.assertEqual(invoice.status, Invoice.Status.PAID)

    def test_inventory_adjust_stock_workflow(self):
        self.authenticate()
        item = InventoryItem.objects.create(
            tenant=self.tenant,
            branch=self.branch,
            name="Standard coffin",
            sku="COFFIN-STD",
            quantity_on_hand=Decimal("2.00"),
        )

        response = self.client.post(
            reverse("inventoryitem-adjust-stock", args=[item.id]),
            {"quantity": "1.00", "transaction_type": "stock_out"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item.refresh_from_db()
        self.assertEqual(item.quantity_on_hand, Decimal("1.00"))

    def test_mortuary_release_workflow(self):
        self.authenticate()
        record = MortuaryRecord.objects.create(
            tenant=self.tenant,
            branch=self.branch,
            case=self.case,
            deceased=self.deceased,
            intake_reference="MOR-001",
            intake_at=timezone.now(),
            created_by=self.user,
        )

        response = self.client.post(reverse("mortuary-record-release", args=[record.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        record.refresh_from_db()
        self.assertEqual(record.status, MortuaryRecord.Status.RELEASED)
