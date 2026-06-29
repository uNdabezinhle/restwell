# Generated for RestWell Sprint 3 financials.

import django.db.models.deletion
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("cases", "0001_initial"),
        ("policies", "0001_initial"),
        ("tenants", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Invoice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("invoice_number", models.CharField(max_length=60)),
                ("customer_name", models.CharField(max_length=180)),
                ("customer_email", models.EmailField(blank=True, max_length=254)),
                ("issue_date", models.DateField()),
                ("due_date", models.DateField()),
                ("status", models.CharField(choices=[("draft", "Draft"), ("issued", "Issued"), ("paid", "Paid"), ("overdue", "Overdue"), ("cancelled", "Cancelled")], default="draft", max_length=20)),
                ("subtotal", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("tax_amount", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("total_amount", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("amount_paid", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("branch", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="invoices", to="tenants.branch")),
                ("case", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="invoices", to="cases.case")),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ("policy_enrollment", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="invoices", to="policies.policyenrollment")),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="invoices", to="tenants.tenant")),
            ],
            options={
                "ordering": ["-issue_date", "-id"],
                "constraints": [models.UniqueConstraint(fields=("tenant", "invoice_number"), name="unique_invoice_number_per_tenant")],
            },
        ),
        migrations.CreateModel(
            name="DebtorAccount",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("customer_name", models.CharField(max_length=180)),
                ("amount_due", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("status", models.CharField(choices=[("open", "Open"), ("settled", "Settled")], default="open", max_length=20)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("invoice", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="debtor_account", to="financials.invoice")),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="debtor_accounts", to="tenants.tenant")),
            ],
            options={"ordering": ["-amount_due", "customer_name"]},
        ),
        migrations.CreateModel(
            name="InvoiceLineItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("description", models.CharField(max_length=220)),
                ("quantity", models.DecimalField(decimal_places=2, default=Decimal("1.00"), max_digits=10)),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("tax_amount", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("line_total", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("invoice", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="line_items", to="financials.invoice")),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="invoice_line_items", to="tenants.tenant")),
            ],
            options={"ordering": ["id"]},
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("method", models.CharField(choices=[("cash", "Cash"), ("card", "Card"), ("eft", "EFT"), ("paystack", "Paystack")], max_length=20)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("completed", "Completed"), ("failed", "Failed")], default="pending", max_length=20)),
                ("provider_reference", models.CharField(blank=True, max_length=120)),
                ("received_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("invoice", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="payments", to="financials.invoice")),
                ("received_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="payments", to="tenants.tenant")),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
