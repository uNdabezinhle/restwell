from datetime import date
from decimal import Decimal

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from cases.models import Case, Deceased
from financials.models import DebtorAccount, Invoice, InvoiceLineItem, Payment
from tenants.models import Branch, Tenant


class FinancialsApiTests(APITestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="RestWell Demo", slug="restwell-demo")
        self.branch = Branch.objects.create(tenant=self.tenant, name="Johannesburg", code="JHB")
        self.other_tenant = Tenant.objects.create(name="Other Care", slug="other-care")
        self.other_branch = Branch.objects.create(tenant=self.other_tenant, name="Cape Town", code="CPT")
        self.user = User.objects.create_user(
            username="finance-admin",
            password="test-password",
            tenant=self.tenant,
            branch=self.branch,
            role=User.Role.TENANT_ADMIN,
        )
        deceased = Deceased.objects.create(tenant=self.tenant, branch=self.branch, first_name="Thabo", last_name="Mokoena")
        self.case = Case.objects.create(tenant=self.tenant, branch=self.branch, deceased=deceased, reference="CASE-001")

    def authenticate(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "finance-admin", "password": "test-password"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def create_invoice(self, tenant=None, branch=None, invoice_number="INV-001"):
        return Invoice.objects.create(
            tenant=tenant or self.tenant,
            branch=branch or self.branch,
            case=self.case if tenant in (None, self.tenant) else None,
            invoice_number=invoice_number,
            customer_name="Lerato Mokoena",
            issue_date=date(2026, 6, 1),
            due_date=date(2026, 6, 30),
            status=Invoice.Status.ISSUED,
        )

    def test_creates_invoice_for_current_tenant(self):
        self.authenticate()

        response = self.client.post(
            reverse("invoice-list"),
            {
                "branch": self.branch.id,
                "case": self.case.id,
                "invoice_number": "INV-100",
                "customer_name": "Lerato Mokoena",
                "issue_date": "2026-06-01",
                "due_date": "2026-06-30",
                "status": Invoice.Status.ISSUED,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["tenant"], self.tenant.id)
        self.assertEqual(response.data["created_by"], self.user.id)

    def test_line_item_updates_invoice_totals_and_debtor(self):
        self.authenticate()
        invoice = self.create_invoice()

        response = self.client.post(
            reverse("invoicelineitem-list"),
            {
                "invoice": invoice.id,
                "description": "Funeral service package",
                "quantity": "2.00",
                "unit_price": "500.00",
                "tax_amount": "150.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        invoice.refresh_from_db()
        self.assertEqual(invoice.subtotal, Decimal("1000.00"))
        self.assertEqual(invoice.total_amount, Decimal("1150.00"))
        self.assertEqual(invoice.debtor_account.amount_due, Decimal("1150.00"))

    def test_completed_payment_marks_invoice_paid(self):
        self.authenticate()
        invoice = self.create_invoice()
        InvoiceLineItem.objects.create(
            tenant=self.tenant,
            invoice=invoice,
            description="Funeral service package",
            quantity="1.00",
            unit_price="1000.00",
            tax_amount="0.00",
        )

        response = self.client.post(
            reverse("payment-list"),
            {
                "invoice": invoice.id,
                "amount": "1000.00",
                "method": Payment.Method.CASH,
                "status": Payment.Status.COMPLETED,
                "received_at": timezone.now().isoformat(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, Invoice.Status.PAID)
        self.assertEqual(invoice.amount_paid, Decimal("1000.00"))
        self.assertEqual(invoice.debtor_account.status, DebtorAccount.Status.SETTLED)

    def test_rejects_cross_tenant_invoice_on_payment(self):
        self.authenticate()
        other_invoice = self.create_invoice(
            tenant=self.other_tenant,
            branch=self.other_branch,
            invoice_number="INV-OTHER",
        )

        response = self.client.post(
            reverse("payment-list"),
            {
                "invoice": other_invoice.id,
                "amount": "100.00",
                "method": Payment.Method.PAYSTACK,
                "status": Payment.Status.PENDING,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_financial_summary_is_tenant_scoped(self):
        self.authenticate()
        invoice = self.create_invoice()
        InvoiceLineItem.objects.create(
            tenant=self.tenant,
            invoice=invoice,
            description="Service",
            quantity="1.00",
            unit_price="500.00",
        )
        other_invoice = self.create_invoice(
            tenant=self.other_tenant,
            branch=self.other_branch,
            invoice_number="INV-OTHER",
        )
        InvoiceLineItem.objects.create(
            tenant=self.other_tenant,
            invoice=other_invoice,
            description="Other",
            quantity="1.00",
            unit_price="999.00",
        )

        response = self.client.get(reverse("financial-summary"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["invoice_count"], 1)
        self.assertEqual(Decimal(str(response.data["total_invoiced"])), Decimal("500.00"))
