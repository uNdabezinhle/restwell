from django.conf import settings
from django.db import models


class MortuaryRecord(models.Model):
    class Status(models.TextChoices):
        INTAKE = "intake", "Intake"
        IN_STORAGE = "in_storage", "In Storage"
        IN_PREPARATION = "in_preparation", "In Preparation"
        READY_FOR_RELEASE = "ready_for_release", "Ready For Release"
        RELEASED = "released", "Released"

    tenant = models.ForeignKey("tenants.Tenant", related_name="mortuary_records", on_delete=models.CASCADE)
    branch = models.ForeignKey("tenants.Branch", related_name="mortuary_records", on_delete=models.PROTECT)
    case = models.ForeignKey("cases.Case", related_name="mortuary_records", null=True, blank=True, on_delete=models.PROTECT)
    deceased = models.ForeignKey("cases.Deceased", related_name="mortuary_records", on_delete=models.PROTECT)
    intake_reference = models.CharField(max_length=60)
    status = models.CharField(max_length=40, choices=Status.choices, default=Status.INTAKE)
    storage_location = models.CharField(max_length=120, blank=True)
    storage_unit = models.CharField(max_length=80, blank=True)
    intake_at = models.DateTimeField()
    released_at = models.DateTimeField(null=True, blank=True)
    preparation_notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-intake_at"]
        constraints = [
            models.UniqueConstraint(fields=["tenant", "intake_reference"], name="unique_mortuary_intake_reference_per_tenant"),
        ]

    def __str__(self):
        return self.intake_reference


class PreparationTask(models.Model):
    class TaskType(models.TextChoices):
        WASHING = "washing", "Washing"
        EMBALMING = "embalming", "Embalming"
        DRESSING = "dressing", "Dressing"
        COSMETICS = "cosmetics", "Cosmetics"
        QUALITY_CHECK = "quality_check", "Quality Check"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        TODO = "todo", "To Do"
        IN_PROGRESS = "in_progress", "In Progress"
        DONE = "done", "Done"
        BLOCKED = "blocked", "Blocked"

    tenant = models.ForeignKey("tenants.Tenant", related_name="preparation_tasks", on_delete=models.CASCADE)
    mortuary_record = models.ForeignKey(MortuaryRecord, related_name="preparation_tasks", on_delete=models.CASCADE)
    task_type = models.CharField(max_length=40, choices=TaskType.choices, default=TaskType.OTHER)
    status = models.CharField(max_length=40, choices=Status.choices, default=Status.TODO)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    due_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["mortuary_record", "due_at", "task_type"]

    def __str__(self):
        return f"{self.mortuary_record}: {self.task_type}"
