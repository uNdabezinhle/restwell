from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("website_builder", "0001_initial"),
        ("tenants", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="WebsiteBlock",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "block_type",
                    models.CharField(
                        choices=[
                            ("hero", "Hero"),
                            ("text", "Text"),
                            ("services", "Services"),
                            ("contact", "Contact"),
                            ("memorial", "Memorial"),
                            ("gallery", "Gallery"),
                            ("cta", "Call To Action"),
                            ("service_schedule", "Service Schedule"),
                            ("inquiry_form", "Inquiry Form"),
                        ],
                        max_length=40,
                    ),
                ),
                ("content", models.JSONField(blank=True, default=dict)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("is_visible", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("page", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="blocks", to="website_builder.websitepage")),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="website_blocks", to="tenants.tenant")),
            ],
            options={"ordering": ["page", "sort_order", "id"]},
        ),
    ]
