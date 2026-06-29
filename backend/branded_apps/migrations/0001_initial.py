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
            name="TenantAppConfig",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("app_name", models.CharField(max_length=80)),
                ("package_name", models.CharField(max_length=120)),
                ("primary_color", models.CharField(default="#0F766E", max_length=7)),
                ("secondary_color", models.CharField(default="#2563EB", max_length=7)),
                ("logo", models.FileField(blank=True, upload_to="branded-apps/logos/")),
                ("support_email", models.EmailField(blank=True, max_length=254)),
                ("privacy_policy_url", models.URLField(blank=True)),
                ("version_name", models.CharField(default="0.1.0", max_length=20)),
                ("version_code", models.PositiveIntegerField(default=1)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("tenant", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="app_config", to="tenants.tenant")),
            ],
            options={
                "ordering": ["tenant__name"],
            },
        ),
        migrations.CreateModel(
            name="AppBuildRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("platform", models.CharField(choices=[("android", "Android")], default="android", max_length=20)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("queued", "Queued"),
                            ("in_progress", "In Progress"),
                            ("succeeded", "Succeeded"),
                            ("failed", "Failed"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="queued",
                        max_length=40,
                    ),
                ),
                ("git_ref", models.CharField(blank=True, max_length=120)),
                ("workflow_run_url", models.URLField(blank=True)),
                ("artifact_url", models.URLField(blank=True)),
                ("error_message", models.TextField(blank=True)),
                ("requested_at", models.DateTimeField(auto_now_add=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("app_config", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="build_requests", to="branded_apps.tenantappconfig")),
                ("requested_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="app_build_requests", to="tenants.tenant")),
            ],
            options={
                "ordering": ["-requested_at"],
            },
        ),
    ]
