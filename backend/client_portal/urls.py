from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ClientSupportRequestViewSet, client_dashboard, mark_notification_read

router = DefaultRouter()
router.register("support-requests", ClientSupportRequestViewSet, basename="client-support-request")

urlpatterns = [
    path("dashboard/", client_dashboard, name="client-dashboard"),
    path("notifications/<int:pk>/mark-read/", mark_notification_read, name="client-notification-mark-read"),
] + router.urls
