from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("cases", "0001_initial"),
        ("tenants", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="LocationRoute",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=180)),
                (
                    "status",
                    models.CharField(
                        choices=[("planned", "Planned"), ("active", "Active"), ("completed", "Completed"), ("cancelled", "Cancelled")],
                        default="planned",
                        max_length=40,
                    ),
                ),
                ("origin", models.CharField(blank=True, max_length=220)),
                ("destination", models.CharField(blank=True, max_length=220)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("ended_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("assigned_to", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ("branch", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="location_routes", to="tenants.branch")),
                ("case", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="location_routes", to="cases.case")),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="location_routes", to="tenants.tenant")),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="LocationLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("latitude", models.DecimalField(decimal_places=6, max_digits=9)),
                ("longitude", models.DecimalField(decimal_places=6, max_digits=9)),
                ("accuracy_meters", models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True)),
                ("recorded_at", models.DateTimeField()),
                ("note", models.CharField(blank=True, max_length=220)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("case", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="location_logs", to="cases.case")),
                ("route", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="logs", to="geolocation.locationroute")),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="location_logs", to="tenants.tenant")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="location_logs", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-recorded_at"],
            },
        ),
        migrations.AddIndex(
            model_name="locationlog",
            index=models.Index(fields=["tenant", "recorded_at"], name="location_log_tenant_time_idx"),
        ),
    ]
