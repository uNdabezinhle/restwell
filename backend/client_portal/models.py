from django.conf import settings
from django.db import models


class ClientSupportRequest(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        RESOLVED = "resolved", "Resolved"

    tenant = models.ForeignKey("tenants.Tenant", related_name="client_support_requests", on_delete=models.CASCADE)
    family_member = models.ForeignKey("cases.FamilyMember", related_name="support_requests", null=True, blank=True, on_delete=models.SET_NULL)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="client_support_requests", null=True, blank=True, on_delete=models.SET_NULL)
    subject = models.CharField(max_length=180)
    message = models.TextField()
    status = models.CharField(max_length=40, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.subject
