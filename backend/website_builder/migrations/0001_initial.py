from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("tenants", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="WebsiteSite",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=180)),
                ("subdomain", models.SlugField(blank=True, max_length=80)),
                ("custom_domain", models.CharField(blank=True, max_length=180)),
                ("is_published", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "tenant",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="website_site", to="tenants.tenant"),
                ),
            ],
            options={
                "ordering": ["tenant__name"],
            },
        ),
        migrations.CreateModel(
            name="WebsitePage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.SlugField(max_length=120)),
                ("title", models.CharField(max_length=180)),
                (
                    "page_type",
                    models.CharField(
                        choices=[
                            ("home", "Home"),
                            ("services", "Services"),
                            ("memorial", "Memorial"),
                            ("contact", "Contact"),
                            ("custom", "Custom"),
                        ],
                        default="custom",
                        max_length=40,
                    ),
                ),
                ("content", models.JSONField(blank=True, default=dict)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("is_published", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "site",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="pages", to="website_builder.websitesite"),
                ),
                (
                    "tenant",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="website_pages", to="tenants.tenant"),
                ),
            ],
            options={
                "ordering": ["site", "sort_order", "title"],
            },
        ),
        migrations.AddConstraint(
            model_name="websitepage",
            constraint=models.UniqueConstraint(fields=("site", "slug"), name="unique_website_page_slug_per_site"),
        ),
    ]
