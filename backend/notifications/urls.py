from rest_framework.routers import DefaultRouter

from .views import (
    NotificationDeliveryLogViewSet,
    NotificationInboxViewSet,
    NotificationMessageViewSet,
    NotificationTemplateViewSet,
)

router = DefaultRouter()
router.register("templates", NotificationTemplateViewSet, basename="notification-template")
router.register("messages", NotificationMessageViewSet, basename="notification-message")
router.register("inbox", NotificationInboxViewSet, basename="notification-inbox")
router.register("delivery-logs", NotificationDeliveryLogViewSet, basename="notification-delivery-log")

urlpatterns = router.urls
