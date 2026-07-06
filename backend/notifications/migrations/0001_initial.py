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
            name="NotificationTemplate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.SlugField(max_length=100)),
                ("channel", models.CharField(choices=[("in_app", "In App"), ("email", "Email"), ("sms", "SMS"), ("whatsapp", "WhatsApp")], max_length=20)),
                ("subject", models.CharField(blank=True, max_length=180)),
                ("body", models.TextField()),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("tenant", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="notification_templates", to="tenants.tenant")),
            ],
            options={"ordering": ["code", "channel"]},
        ),
        migrations.CreateModel(
            name="NotificationMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("recipient_name", models.CharField(blank=True, max_length=180)),
                ("recipient_email", models.EmailField(blank=True, max_length=254)),
                ("recipient_phone", models.CharField(blank=True, max_length=40)),
                ("channel", models.CharField(choices=[("in_app", "In App"), ("email", "Email"), ("sms", "SMS"), ("whatsapp", "WhatsApp")], max_length=20)),
                ("subject", models.CharField(blank=True, max_length=180)),
                ("body", models.TextField()),
                ("status", models.CharField(choices=[("queued", "Queued"), ("sent", "Sent"), ("failed", "Failed"), ("read", "Read")], default="queued", max_length=20)),
                ("provider_response", models.JSONField(blank=True, default=dict)),
                ("retry_count", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("sent_at", models.DateTimeField(blank=True, null=True)),
                ("read_at", models.DateTimeField(blank=True, null=True)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_notifications", to=settings.AUTH_USER_MODEL)),
                ("recipient_user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="notification_messages", to=settings.AUTH_USER_MODEL)),
                ("template", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="messages", to="notifications.notificationtemplate")),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notification_messages", to="tenants.tenant")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="NotificationDeliveryLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("provider", models.CharField(default="local", max_length=80)),
                ("status", models.CharField(max_length=40)),
                ("response", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("message", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="delivery_logs", to="notifications.notificationmessage")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddConstraint(
            model_name="notificationtemplate",
            constraint=models.UniqueConstraint(fields=("tenant", "code", "channel"), name="unique_notification_template_per_tenant_channel"),
        ),
    ]
