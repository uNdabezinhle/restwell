from django.conf import settings
from django.db import models


class TenantAppConfig(models.Model):
    tenant = models.OneToOneField("tenants.Tenant", related_name="app_config", on_delete=models.CASCADE)
    app_name = models.CharField(max_length=80)
    package_name = models.CharField(max_length=120)
    primary_color = models.CharField(max_length=7, default="#0F766E")
    secondary_color = models.CharField(max_length=7, default="#2563EB")
    logo = models.FileField(upload_to="branded-apps/logos/", blank=True)
    support_email = models.EmailField(blank=True)
    privacy_policy_url = models.URLField(blank=True)
    version_name = models.CharField(max_length=20, default="0.1.0")
    version_code = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["tenant__name"]

    def __str__(self):
        return f"{self.tenant} Android app"


class AppBuildRequest(models.Model):
    class Platform(models.TextChoices):
        ANDROID = "android", "Android"

    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        IN_PROGRESS = "in_progress", "In Progress"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    tenant = models.ForeignKey("tenants.Tenant", related_name="app_build_requests", on_delete=models.CASCADE)
    app_config = models.ForeignKey(TenantAppConfig, related_name="build_requests", on_delete=models.PROTECT)
    platform = models.CharField(max_length=20, choices=Platform.choices, default=Platform.ANDROID)
    status = models.CharField(max_length=40, choices=Status.choices, default=Status.QUEUED)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    git_ref = models.CharField(max_length=120, blank=True)
    workflow_run_url = models.URLField(blank=True)
    artifact_url = models.URLField(blank=True)
    error_message = models.TextField(blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-requested_at"]

    def __str__(self):
        return f"{self.app_config.app_name} {self.platform} build"
