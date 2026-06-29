# Generated for RestWell Sprint 4 scheduling.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("cases", "0001_initial"),
        ("tenants", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Resource",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=180)),
                ("resource_type", models.CharField(choices=[("vehicle", "Vehicle"), ("staff", "Staff"), ("venue", "Venue"), ("equipment", "Equipment")], max_length=30)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("branch", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="resources", to="tenants.branch")),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="resources", to="tenants.tenant")),
            ],
            options={"ordering": ["resource_type", "name"]},
        ),
        migrations.CreateModel(
            name="CalendarEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=180)),
                ("event_type", models.CharField(choices=[("funeral_service", "Funeral Service"), ("pickup", "Pickup"), ("meeting", "Meeting"), ("other", "Other")], default="other", max_length=40)),
                ("starts_at", models.DateTimeField()),
                ("ends_at", models.DateTimeField()),
                ("location", models.CharField(blank=True, max_length=180)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("branch", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="calendar_events", to="tenants.branch")),
                ("case", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="calendar_events", to="cases.case")),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ("resources", models.ManyToManyField(blank=True, related_name="calendar_events", to="scheduling.resource")),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="calendar_events", to="tenants.tenant")),
            ],
            options={"ordering": ["starts_at"]},
        ),
    ]
