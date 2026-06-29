from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("tenants", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="TenantOnboardingStatus",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "status",
                    models.CharField(
                        choices=[("not_started", "Not Started"), ("in_progress", "In Progress"), ("completed", "Completed")],
                        default="not_started",
                        max_length=40,
                    ),
                ),
                ("current_step", models.CharField(blank=True, max_length=120)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("tenant", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="onboarding_status", to="tenants.tenant")),
            ],
            options={
                "ordering": ["tenant__name"],
            },
        ),
        migrations.CreateModel(
            name="OnboardingTask",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=160)),
                ("description", models.TextField(blank=True)),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("platform_setup", "Platform Setup"),
                            ("users", "Users"),
                            ("branding", "Branding"),
                            ("cases", "Cases"),
                            ("policies", "Policies"),
                            ("training", "Training"),
                        ],
                        default="platform_setup",
                        max_length=40,
                    ),
                ),
                ("is_required", models.BooleanField(default=True)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("completed_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="onboarding_tasks", to="tenants.tenant")),
            ],
            options={
                "ordering": ["sort_order", "title"],
            },
        ),
        migrations.CreateModel(
            name="HelpArticle",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.SlugField(max_length=140)),
                ("title", models.CharField(max_length=180)),
                ("summary", models.CharField(blank=True, max_length=240)),
                ("body", models.TextField()),
                ("category", models.CharField(default="getting-started", max_length=80)),
                (
                    "audience",
                    models.CharField(
                        choices=[("all", "All"), ("tenant_admin", "Tenant Admin"), ("staff", "Staff"), ("family", "Family")],
                        default="all",
                        max_length=40,
                    ),
                ),
                ("is_published", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("tenant", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="help_articles", to="tenants.tenant")),
            ],
            options={
                "ordering": ["category", "title"],
            },
        ),
        migrations.AddConstraint(
            model_name="onboardingtask",
            constraint=models.UniqueConstraint(fields=("tenant", "title"), name="unique_onboarding_task_title_per_tenant"),
        ),
        migrations.AddConstraint(
            model_name="helparticle",
            constraint=models.UniqueConstraint(fields=("tenant", "slug"), name="unique_help_article_slug_per_tenant"),
        ),
    ]
