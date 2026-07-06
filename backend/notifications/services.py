from django.utils import timezone

from .models import NotificationDeliveryLog, NotificationMessage


def send_notification(message, provider="local"):
    message.status = NotificationMessage.Status.SENT
    message.sent_at = timezone.now()
    message.provider_response = {
        "provider": provider,
        "mode": "local",
        "detail": "Notification recorded locally for development.",
    }
    message.save(update_fields=["status", "sent_at", "provider_response"])
    NotificationDeliveryLog.objects.create(
        message=message,
        provider=provider,
        status=message.status,
        response=message.provider_response,
    )
    return message
