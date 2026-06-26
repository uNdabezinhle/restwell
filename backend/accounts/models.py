from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        SUPER_ADMIN = "super_admin", "Super Admin"
        TENANT_ADMIN = "tenant_admin", "Tenant Admin"
        STAFF = "staff", "Staff"
        UNDERWRITER = "underwriter", "Underwriter"
        FAMILY = "family", "Family"

    tenant = models.ForeignKey("tenants.Tenant", null=True, blank=True, on_delete=models.PROTECT)
    branch = models.ForeignKey("tenants.Branch", null=True, blank=True, on_delete=models.PROTECT)
    role = models.CharField(max_length=40, choices=Role.choices, default=Role.STAFF)

    @property
    def is_platform_admin(self):
        return self.is_superuser or self.role == self.Role.SUPER_ADMIN
