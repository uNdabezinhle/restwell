# Generated for RestWell Sprint 2 policy management.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("cases", "0001_initial"),
        ("tenants", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Underwriter",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=180)),
                ("registration_number", models.CharField(blank=True, max_length=80)),
                ("contact_email", models.EmailField(blank=True, max_length=254)),
                ("contact_phone", models.CharField(blank=True, max_length=40)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="underwriters", to="tenants.tenant")),
            ],
            options={
                "ordering": ["name"],
                "constraints": [models.UniqueConstraint(fields=("tenant", "name"), name="unique_underwriter_name_per_tenant")],
            },
        ),
        migrations.CreateModel(
            name="PolicyTemplate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=180)),
                ("description", models.TextField(blank=True)),
                ("cover_amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("premium_amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("billing_frequency", models.CharField(choices=[("monthly", "Monthly"), ("annual", "Annual")], default="monthly", max_length=20)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="policy_templates", to="tenants.tenant")),
                ("underwriter", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="policy_templates", to="policies.underwriter")),
            ],
            options={
                "ordering": ["name"],
                "constraints": [models.UniqueConstraint(fields=("tenant", "name"), name="unique_policy_template_name_per_tenant")],
            },
        ),
        migrations.CreateModel(
            name="PolicyEnrollment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("policy_number", models.CharField(max_length=60)),
                ("status", models.CharField(choices=[("active", "Active"), ("lapsed", "Lapsed"), ("cancelled", "Cancelled")], default="active", max_length=20)),
                ("start_date", models.DateField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ("family_member", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="policy_enrollments", to="cases.familymember")),
                ("policy_template", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="enrollments", to="policies.policytemplate")),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="policy_enrollments", to="tenants.tenant")),
                ("underwriter", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="enrollments", to="policies.underwriter")),
            ],
            options={
                "ordering": ["-created_at"],
                "constraints": [models.UniqueConstraint(fields=("tenant", "policy_number"), name="unique_policy_number_per_tenant")],
            },
        ),
        migrations.CreateModel(
            name="PremiumPayment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("due_date", models.DateField()),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("paid", "Paid"), ("failed", "Failed")], default="pending", max_length=20)),
                ("reference", models.CharField(blank=True, max_length=80)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("enrollment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="premium_payments", to="policies.policyenrollment")),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="premium_payments", to="tenants.tenant")),
            ],
            options={"ordering": ["due_date", "id"]},
        ),
    ]
