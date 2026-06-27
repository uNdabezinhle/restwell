# Generated for RestWell Sprint 1 case management.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("tenants", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Deceased",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("first_name", models.CharField(max_length=120)),
                ("last_name", models.CharField(max_length=120)),
                ("id_number", models.CharField(blank=True, max_length=40)),
                ("date_of_birth", models.DateField(blank=True, null=True)),
                ("date_of_death", models.DateField(blank=True, null=True)),
                ("place_of_death", models.CharField(blank=True, max_length=180)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("branch", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="deceased_records", to="tenants.branch")),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="deceased_records", to="tenants.tenant")),
            ],
            options={"ordering": ["last_name", "first_name"]},
        ),
        migrations.CreateModel(
            name="Case",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("reference", models.CharField(max_length=40)),
                ("status", models.CharField(choices=[("new", "New"), ("in_progress", "In Progress"), ("completed", "Completed")], default="new", max_length=32)),
                ("service_date", models.DateField(blank=True, null=True)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("branch", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="cases", to="tenants.branch")),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ("deceased", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="cases", to="cases.deceased")),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="cases", to="tenants.tenant")),
            ],
            options={
                "ordering": ["-created_at"],
                "constraints": [models.UniqueConstraint(fields=("tenant", "reference"), name="unique_case_reference_per_tenant")],
            },
        ),
        migrations.CreateModel(
            name="CaseDocument",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("document_type", models.CharField(choices=[("bi1663", "BI1663"), ("coc", "Certificate of Competence"), ("id_copy", "ID Copy"), ("other", "Other")], default="other", max_length=32)),
                ("title", models.CharField(max_length=180)),
                ("file", models.FileField(blank=True, upload_to="case-documents/%Y/%m/")),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                ("case", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="documents", to="cases.case")),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="case_documents", to="tenants.tenant")),
                ("uploaded_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-uploaded_at"]},
        ),
        migrations.CreateModel(
            name="FamilyMember",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("first_name", models.CharField(max_length=120)),
                ("last_name", models.CharField(max_length=120)),
                ("relationship", models.CharField(max_length=80)),
                ("phone", models.CharField(blank=True, max_length=40)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("is_next_of_kin", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("case", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="family_members", to="cases.case")),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="family_members", to="tenants.tenant")),
            ],
            options={"ordering": ["-is_next_of_kin", "last_name", "first_name"]},
        ),
    ]
