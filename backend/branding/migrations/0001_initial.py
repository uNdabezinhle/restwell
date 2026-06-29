from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("tenants", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="TenantBranding",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("logo", models.FileField(blank=True, upload_to="branding/logos/")),
                ("primary_color", models.CharField(default="#0F766E", max_length=7)),
                ("secondary_color", models.CharField(default="#2563EB", max_length=7)),
                ("email_from_name", models.CharField(blank=True, max_length=120)),
                ("sms_sender_name", models.CharField(blank=True, max_length=40)),
                ("custom_domain", models.CharField(blank=True, max_length=180)),
                ("remove_powered_by", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "tenant",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="branding", to="tenants.tenant"),
                ),
            ],
            options={
                "ordering": ["tenant__name"],
            },
        ),
    ]
