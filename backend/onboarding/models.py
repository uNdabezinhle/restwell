from django.conf import settings
from django.db import models


class TenantOnboardingStatus(models.Model):
    class Status(models.TextChoices):
        NOT_STARTED = "not_started", "Not Started"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"

    tenant = models.OneToOneField("tenants.Tenant", related_name="onboarding_status", on_delete=models.CASCADE)
    status = models.CharField(max_length=40, choices=Status.choices, default=Status.NOT_STARTED)
    current_step = models.CharField(max_length=120, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["tenant__name"]

    def __str__(self):
        return f"{self.tenant} onboarding"


class OnboardingTask(models.Model):
    class Category(models.TextChoices):
        PLATFORM_SETUP = "platform_setup", "Platform Setup"
        USERS = "users", "Users"
        BRANDING = "branding", "Branding"
        CASES = "cases", "Cases"
        POLICIES = "policies", "Policies"
        TRAINING = "training", "Training"

    tenant = models.ForeignKey("tenants.Tenant", related_name="onboarding_tasks", on_delete=models.CASCADE)
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=40, choices=Category.choices, default=Category.PLATFORM_SETUP)
    is_required = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    completed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "title"]
        constraints = [
            models.UniqueConstraint(fields=["tenant", "title"], name="unique_onboarding_task_title_per_tenant"),
        ]

    def __str__(self):
        return self.title

    @property
    def is_completed(self):
        return self.completed_at is not None


class HelpArticle(models.Model):
    class Audience(models.TextChoices):
        ALL = "all", "All"
        TENANT_ADMIN = "tenant_admin", "Tenant Admin"
        STAFF = "staff", "Staff"
        FAMILY = "family", "Family"

    tenant = models.ForeignKey("tenants.Tenant", related_name="help_articles", null=True, blank=True, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=140)
    title = models.CharField(max_length=180)
    summary = models.CharField(max_length=240, blank=True)
    body = models.TextField()
    category = models.CharField(max_length=80, default="getting-started")
    audience = models.CharField(max_length=40, choices=Audience.choices, default=Audience.ALL)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "title"]
        constraints = [
            models.UniqueConstraint(fields=["tenant", "slug"], name="unique_help_article_slug_per_tenant"),
        ]

    def __str__(self):
        return self.title
