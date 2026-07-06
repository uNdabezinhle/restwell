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
            name="TenantFeature",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(choices=[("mortuary", "Mortuary"), ("geolocation", "Geolocation"), ("website_builder", "Website Builder"), ("branded_apps", "Branded Apps"), ("notifications", "Notifications")], max_length=60)),
                ("is_enabled", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="features", to="tenants.tenant")),
            ],
            options={"ordering": ["tenant__name", "code"]},
        ),
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("action", models.CharField(choices=[("create", "Create"), ("update", "Update"), ("delete", "Delete"), ("workflow", "Workflow"), ("access", "Access")], max_length=40)),
                ("resource_type", models.CharField(max_length=120)),
                ("resource_id", models.CharField(blank=True, max_length=80)),
                ("description", models.CharField(blank=True, max_length=240)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("actor", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ("tenant", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="audit_logs", to="tenants.tenant")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="ConsentRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("subject_name", models.CharField(max_length=180)),
                ("subject_email", models.EmailField(blank=True, max_length=254)),
                ("purpose", models.CharField(max_length=160)),
                ("granted", models.BooleanField(default=True)),
                ("source", models.CharField(blank=True, max_length=120)),
                ("recorded_at", models.DateTimeField(auto_now_add=True)),
                ("recorded_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="consent_records", to="tenants.tenant")),
            ],
            options={"ordering": ["-recorded_at"]},
        ),
        migrations.CreateModel(
            name="DataSubjectRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("request_type", models.CharField(choices=[("access", "Access"), ("export", "Export"), ("correction", "Correction"), ("deletion", "Deletion")], max_length=40)),
                ("status", models.CharField(choices=[("open", "Open"), ("in_progress", "In Progress"), ("completed", "Completed"), ("rejected", "Rejected")], default="open", max_length=40)),
                ("subject_name", models.CharField(max_length=180)),
                ("subject_email", models.EmailField(blank=True, max_length=254)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("assigned_to", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="data_subject_requests", to="tenants.tenant")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddConstraint(
            model_name="tenantfeature",
            constraint=models.UniqueConstraint(fields=("tenant", "code"), name="unique_feature_code_per_tenant"),
        ),
    ]
