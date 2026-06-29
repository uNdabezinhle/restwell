from django.conf import settings
from django.db import models


class LocationRoute(models.Model):
    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    tenant = models.ForeignKey("tenants.Tenant", related_name="location_routes", on_delete=models.CASCADE)
    branch = models.ForeignKey("tenants.Branch", related_name="location_routes", on_delete=models.PROTECT)
    case = models.ForeignKey("cases.Case", related_name="location_routes", null=True, blank=True, on_delete=models.PROTECT)
    name = models.CharField(max_length=180)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=40, choices=Status.choices, default=Status.PLANNED)
    origin = models.CharField(max_length=220, blank=True)
    destination = models.CharField(max_length=220, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class LocationLog(models.Model):
    tenant = models.ForeignKey("tenants.Tenant", related_name="location_logs", on_delete=models.CASCADE)
    route = models.ForeignKey(LocationRoute, related_name="logs", null=True, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="location_logs", on_delete=models.PROTECT)
    case = models.ForeignKey("cases.Case", related_name="location_logs", null=True, blank=True, on_delete=models.PROTECT)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    accuracy_meters = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    recorded_at = models.DateTimeField()
    note = models.CharField(max_length=220, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at"]
        indexes = [
            models.Index(fields=["tenant", "recorded_at"], name="location_log_tenant_time_idx"),
        ]

    def __str__(self):
        return f"{self.user} @ {self.recorded_at}"
