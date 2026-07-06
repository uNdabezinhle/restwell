from django.conf import settings
from django.db import models


class TenantFeature(models.Model):
    class Code(models.TextChoices):
        MORTUARY = "mortuary", "Mortuary"
        GEOLOCATION = "geolocation", "Geolocation"
        WEBSITE_BUILDER = "website_builder", "Website Builder"
        BRANDED_APPS = "branded_apps", "Branded Apps"
        NOTIFICATIONS = "notifications", "Notifications"

    tenant = models.ForeignKey("tenants.Tenant", related_name="features", on_delete=models.CASCADE)
    code = models.CharField(max_length=60, choices=Code.choices)
    is_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["tenant__name", "code"]
        constraints = [
            models.UniqueConstraint(fields=["tenant", "code"], name="unique_feature_code_per_tenant"),
        ]

    def __str__(self):
        return f"{self.tenant}: {self.code}"


class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATE = "create", "Create"
        UPDATE = "update", "Update"
        DELETE = "delete", "Delete"
        WORKFLOW = "workflow", "Workflow"
        ACCESS = "access", "Access"

    tenant = models.ForeignKey("tenants.Tenant", related_name="audit_logs", null=True, blank=True, on_delete=models.SET_NULL)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=40, choices=Action.choices)
    resource_type = models.CharField(max_length=120)
    resource_id = models.CharField(max_length=80, blank=True)
    description = models.CharField(max_length=240, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} {self.resource_type} {self.resource_id}"


class ConsentRecord(models.Model):
    tenant = models.ForeignKey("tenants.Tenant", related_name="consent_records", on_delete=models.CASCADE)
    subject_name = models.CharField(max_length=180)
    subject_email = models.EmailField(blank=True)
    purpose = models.CharField(max_length=160)
    granted = models.BooleanField(default=True)
    source = models.CharField(max_length=120, blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at"]


class DataSubjectRequest(models.Model):
    class RequestType(models.TextChoices):
        ACCESS = "access", "Access"
        EXPORT = "export", "Export"
        CORRECTION = "correction", "Correction"
        DELETION = "deletion", "Deletion"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        REJECTED = "rejected", "Rejected"

    tenant = models.ForeignKey("tenants.Tenant", related_name="data_subject_requests", on_delete=models.CASCADE)
    request_type = models.CharField(max_length=40, choices=RequestType.choices)
    status = models.CharField(max_length=40, choices=Status.choices, default=Status.OPEN)
    subject_name = models.CharField(max_length=180)
    subject_email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
