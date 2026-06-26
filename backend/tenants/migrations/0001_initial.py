# Generated for RestWell Sprint 0 foundation.

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Tenant",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=180)),
                ("slug", models.SlugField(unique=True)),
                ("legal_name", models.CharField(blank=True, max_length=220)),
                ("registration_number", models.CharField(blank=True, max_length=80)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Branch",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=180)),
                ("code", models.CharField(max_length=40)),
                ("province", models.CharField(blank=True, max_length=80)),
                ("city", models.CharField(blank=True, max_length=100)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="branches", to="tenants.tenant")),
            ],
            options={
                "ordering": ["tenant__name", "name"],
                "constraints": [
                    models.UniqueConstraint(fields=("tenant", "code"), name="unique_branch_code_per_tenant"),
                ],
            },
        ),
    ]
