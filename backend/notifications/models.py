from django.conf import settings
from django.db import models


class NotificationTemplate(models.Model):
    class Channel(models.TextChoices):
        IN_APP = "in_app", "In App"
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"
        WHATSAPP = "whatsapp", "WhatsApp"

    tenant = models.ForeignKey("tenants.Tenant", related_name="notification_templates", null=True, blank=True, on_delete=models.CASCADE)
    code = models.SlugField(max_length=100)
    channel = models.CharField(max_length=20, choices=Channel.choices)
    subject = models.CharField(max_length=180, blank=True)
    body = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code", "channel"]
        constraints = [
            models.UniqueConstraint(fields=["tenant", "code", "channel"], name="unique_notification_template_per_tenant_channel"),
        ]

    def __str__(self):
        return f"{self.code} ({self.channel})"


class NotificationMessage(models.Model):
    class Channel(models.TextChoices):
        IN_APP = "in_app", "In App"
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"
        WHATSAPP = "whatsapp", "WhatsApp"

    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"
        READ = "read", "Read"

    tenant = models.ForeignKey("tenants.Tenant", related_name="notification_messages", on_delete=models.CASCADE)
    template = models.ForeignKey(NotificationTemplate, related_name="messages", null=True, blank=True, on_delete=models.SET_NULL)
    recipient_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="notification_messages", null=True, blank=True, on_delete=models.SET_NULL)
    recipient_name = models.CharField(max_length=180, blank=True)
    recipient_email = models.EmailField(blank=True)
    recipient_phone = models.CharField(max_length=40, blank=True)
    channel = models.CharField(max_length=20, choices=Channel.choices)
    subject = models.CharField(max_length=180, blank=True)
    body = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED)
    provider_response = models.JSONField(default=dict, blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="created_notifications", null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.channel} {self.recipient_name or self.recipient_email or self.recipient_phone}"


class NotificationDeliveryLog(models.Model):
    message = models.ForeignKey(NotificationMessage, related_name="delivery_logs", on_delete=models.CASCADE)
    provider = models.CharField(max_length=80, default="local")
    status = models.CharField(max_length=40)
    response = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
