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
            name="MortuaryRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("intake_reference", models.CharField(max_length=60)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("intake", "Intake"),
                            ("in_storage", "In Storage"),
                            ("in_preparation", "In Preparation"),
                            ("ready_for_release", "Ready For Release"),
                            ("released", "Released"),
                        ],
                        default="intake",
                        max_length=40,
                    ),
                ),
                ("storage_location", models.CharField(blank=True, max_length=120)),
                ("storage_unit", models.CharField(blank=True, max_length=80)),
                ("intake_at", models.DateTimeField()),
                ("released_at", models.DateTimeField(blank=True, null=True)),
                ("preparation_notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("branch", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="mortuary_records", to="tenants.branch")),
                ("case", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="mortuary_records", to="cases.case")),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ("deceased", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="mortuary_records", to="cases.deceased")),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="mortuary_records", to="tenants.tenant")),
            ],
            options={
                "ordering": ["-intake_at"],
            },
        ),
        migrations.CreateModel(
            name="PreparationTask",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "task_type",
                    models.CharField(
                        choices=[
                            ("washing", "Washing"),
                            ("embalming", "Embalming"),
                            ("dressing", "Dressing"),
                            ("cosmetics", "Cosmetics"),
                            ("quality_check", "Quality Check"),
                            ("other", "Other"),
                        ],
                        default="other",
                        max_length=40,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("todo", "To Do"), ("in_progress", "In Progress"), ("done", "Done"), ("blocked", "Blocked")],
                        default="todo",
                        max_length=40,
                    ),
                ),
                ("due_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("assigned_to", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ("mortuary_record", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="preparation_tasks", to="mortuary.mortuaryrecord")),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="preparation_tasks", to="tenants.tenant")),
            ],
            options={
                "ordering": ["mortuary_record", "due_at", "task_type"],
            },
        ),
        migrations.AddConstraint(
            model_name="mortuaryrecord",
            constraint=models.UniqueConstraint(fields=("tenant", "intake_reference"), name="unique_mortuary_intake_reference_per_tenant"),
        ),
    ]
