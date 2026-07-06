from rest_framework import serializers

from .models import NotificationDeliveryLog, NotificationMessage, NotificationTemplate


class NotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = ["id", "tenant", "code", "channel", "subject", "body", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "tenant", "created_at", "updated_at"]


class NotificationDeliveryLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationDeliveryLog
        fields = ["id", "message", "provider", "status", "response", "created_at"]
        read_only_fields = fields


class NotificationMessageSerializer(serializers.ModelSerializer):
    delivery_logs = NotificationDeliveryLogSerializer(many=True, read_only=True)

    class Meta:
        model = NotificationMessage
        fields = [
            "id",
            "tenant",
            "template",
            "recipient_user",
            "recipient_name",
            "recipient_email",
            "recipient_phone",
            "channel",
            "subject",
            "body",
            "status",
            "provider_response",
            "retry_count",
            "created_by",
            "created_at",
            "sent_at",
            "read_at",
            "delivery_logs",
        ]
        read_only_fields = ["id", "tenant", "status", "provider_response", "retry_count", "created_by", "created_at", "sent_at", "read_at", "delivery_logs"]
