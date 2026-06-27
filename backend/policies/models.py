from django.conf import settings
from django.db import models


class Underwriter(models.Model):
    tenant = models.ForeignKey("tenants.Tenant", related_name="underwriters", on_delete=models.CASCADE)
    name = models.CharField(max_length=180)
    registration_number = models.CharField(max_length=80, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=40, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["tenant", "name"], name="unique_underwriter_name_per_tenant"),
        ]

    def __str__(self):
        return self.name


class PolicyTemplate(models.Model):
    class BillingFrequency(models.TextChoices):
        MONTHLY = "monthly", "Monthly"
        ANNUAL = "annual", "Annual"

    tenant = models.ForeignKey("tenants.Tenant", related_name="policy_templates", on_delete=models.CASCADE)
    underwriter = models.ForeignKey(Underwriter, related_name="policy_templates", on_delete=models.PROTECT)
    name = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    cover_amount = models.DecimalField(max_digits=12, decimal_places=2)
    premium_amount = models.DecimalField(max_digits=10, decimal_places=2)
    billing_frequency = models.CharField(max_length=20, choices=BillingFrequency.choices, default=BillingFrequency.MONTHLY)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["tenant", "name"], name="unique_policy_template_name_per_tenant"),
        ]

    def __str__(self):
        return self.name


class PolicyEnrollment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        LAPSED = "lapsed", "Lapsed"
        CANCELLED = "cancelled", "Cancelled"

    tenant = models.ForeignKey("tenants.Tenant", related_name="policy_enrollments", on_delete=models.CASCADE)
    policy_template = models.ForeignKey(PolicyTemplate, related_name="enrollments", on_delete=models.PROTECT)
    underwriter = models.ForeignKey(Underwriter, related_name="enrollments", on_delete=models.PROTECT)
    family_member = models.ForeignKey("cases.FamilyMember", related_name="policy_enrollments", on_delete=models.PROTECT)
    policy_number = models.CharField(max_length=60)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    start_date = models.DateField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["tenant", "policy_number"], name="unique_policy_number_per_tenant"),
        ]

    def __str__(self):
        return self.policy_number


class PremiumPayment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"

    tenant = models.ForeignKey("tenants.Tenant", related_name="premium_payments", on_delete=models.CASCADE)
    enrollment = models.ForeignKey(PolicyEnrollment, related_name="premium_payments", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    paid_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reference = models.CharField(max_length=80, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["due_date", "id"]

    def __str__(self):
        return f"{self.enrollment.policy_number} {self.amount}"
