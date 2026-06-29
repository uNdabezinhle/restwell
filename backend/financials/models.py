from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Sum


class Invoice(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ISSUED = "issued", "Issued"
        PAID = "paid", "Paid"
        OVERDUE = "overdue", "Overdue"
        CANCELLED = "cancelled", "Cancelled"

    tenant = models.ForeignKey("tenants.Tenant", related_name="invoices", on_delete=models.CASCADE)
    branch = models.ForeignKey("tenants.Branch", related_name="invoices", on_delete=models.PROTECT)
    case = models.ForeignKey("cases.Case", related_name="invoices", null=True, blank=True, on_delete=models.PROTECT)
    policy_enrollment = models.ForeignKey(
        "policies.PolicyEnrollment",
        related_name="invoices",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    invoice_number = models.CharField(max_length=60)
    customer_name = models.CharField(max_length=180)
    customer_email = models.EmailField(blank=True)
    issue_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-issue_date", "-id"]
        constraints = [
            models.UniqueConstraint(fields=["tenant", "invoice_number"], name="unique_invoice_number_per_tenant"),
        ]

    @property
    def balance_due(self):
        return self.total_amount - self.amount_paid

    def recalculate_totals(self):
        totals = self.line_items.aggregate(
            subtotal=Sum("line_total"),
            tax_amount=Sum("tax_amount"),
        )
        self.subtotal = totals["subtotal"] or Decimal("0.00")
        self.tax_amount = totals["tax_amount"] or Decimal("0.00")
        self.total_amount = self.subtotal + self.tax_amount
        self.amount_paid = self.payments.filter(status=Payment.Status.COMPLETED).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
        if self.total_amount > Decimal("0.00") and self.amount_paid >= self.total_amount:
            self.status = self.Status.PAID
        elif self.status == self.Status.PAID and self.amount_paid < self.total_amount:
            self.status = self.Status.ISSUED

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        DebtorAccount.objects.update_or_create(
            tenant=self.tenant,
            invoice=self,
            defaults={
                "customer_name": self.customer_name,
                "amount_due": self.balance_due,
                "status": DebtorAccount.Status.SETTLED if self.balance_due <= 0 else DebtorAccount.Status.OPEN,
            },
        )

    def __str__(self):
        return self.invoice_number


class InvoiceLineItem(models.Model):
    tenant = models.ForeignKey("tenants.Tenant", related_name="invoice_line_items", on_delete=models.CASCADE)
    invoice = models.ForeignKey(Invoice, related_name="line_items", on_delete=models.CASCADE)
    description = models.CharField(max_length=220)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("1.00"))
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def save(self, *args, **kwargs):
        self.line_total = Decimal(str(self.quantity)) * Decimal(str(self.unit_price))
        super().save(*args, **kwargs)
        self.invoice.recalculate_totals()
        self.invoice.save(update_fields=["subtotal", "tax_amount", "total_amount", "amount_paid", "status", "updated_at"])

    def __str__(self):
        return self.description


class Payment(models.Model):
    class Method(models.TextChoices):
        CASH = "cash", "Cash"
        CARD = "card", "Card"
        EFT = "eft", "EFT"
        PAYSTACK = "paystack", "Paystack"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    tenant = models.ForeignKey("tenants.Tenant", related_name="payments", on_delete=models.CASCADE)
    invoice = models.ForeignKey(Invoice, related_name="payments", on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=20, choices=Method.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    provider_reference = models.CharField(max_length=120, blank=True)
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    received_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.invoice.recalculate_totals()
        self.invoice.save(update_fields=["subtotal", "tax_amount", "total_amount", "amount_paid", "status", "updated_at"])

    def __str__(self):
        return f"{self.invoice.invoice_number} {self.amount}"


class DebtorAccount(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        SETTLED = "settled", "Settled"

    tenant = models.ForeignKey("tenants.Tenant", related_name="debtor_accounts", on_delete=models.CASCADE)
    invoice = models.OneToOneField(Invoice, related_name="debtor_account", on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=180)
    amount_due = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-amount_due", "customer_name"]

    def __str__(self):
        return f"{self.customer_name} {self.amount_due}"
