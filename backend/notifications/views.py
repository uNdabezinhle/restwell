from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from accounts.permissions import IsTenantAdminOrPlatformAdmin
from platform_core.models import TenantFeature
from platform_core.permissions import HasTenantFeature
from .models import NotificationDeliveryLog, NotificationMessage, NotificationTemplate
from .serializers import NotificationDeliveryLogSerializer, NotificationMessageSerializer, NotificationTemplateSerializer
from .services import send_notification


class TenantScopedNotificationViewSet(ModelViewSet):
    permission_classes = [IsTenantAdminOrPlatformAdmin, HasTenantFeature]
    feature_code = TenantFeature.Code.NOTIFICATIONS

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_platform_admin:
            return queryset
        if user.tenant_id:
            return queryset.filter(tenant_id=user.tenant_id)
        return queryset.none()

    def current_tenant(self):
        if not self.request.user.tenant_id:
            raise ValidationError("A tenant-scoped user is required.")
        return self.request.user.tenant


class NotificationTemplateViewSet(TenantScopedNotificationViewSet):
    queryset = NotificationTemplate.objects.select_related("tenant")
    serializer_class = NotificationTemplateSerializer

    def get_queryset(self):
        queryset = self.queryset.all()
        if self.request.user.is_platform_admin:
            return queryset
        return queryset.filter(tenant__isnull=True) | queryset.filter(tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        serializer.save(tenant=self.current_tenant())


class NotificationMessageViewSet(TenantScopedNotificationViewSet):
    queryset = NotificationMessage.objects.select_related("tenant", "template", "recipient_user", "created_by").prefetch_related("delivery_logs")
    serializer_class = NotificationMessageSerializer

    def perform_create(self, serializer):
        tenant = self.current_tenant()
        template = serializer.validated_data.get("template")
        recipient_user = serializer.validated_data.get("recipient_user")
        if template and template.tenant_id not in (None, tenant.id):
            raise ValidationError({"template": "Template must be global or belong to the current tenant."})
        if recipient_user and recipient_user.tenant_id != tenant.id:
            raise ValidationError({"recipient_user": "Recipient user must belong to the current tenant."})
        serializer.save(tenant=tenant, created_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="send")
    def send(self, request, pk=None):
        message = send_notification(self.get_object())
        return Response(self.get_serializer(message).data)

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        message = self.get_object()
        message.status = NotificationMessage.Status.READ
        message.read_at = timezone.now()
        message.save(update_fields=["status", "read_at"])
        return Response(self.get_serializer(message).data)


class NotificationInboxViewSet(ReadOnlyModelViewSet):
    serializer_class = NotificationMessageSerializer
    permission_classes = [IsTenantAdminOrPlatformAdmin, HasTenantFeature]
    feature_code = TenantFeature.Code.NOTIFICATIONS

    def get_queryset(self):
        return NotificationMessage.objects.filter(recipient_user=self.request.user).select_related("tenant", "template", "recipient_user", "created_by")


class NotificationDeliveryLogViewSet(ReadOnlyModelViewSet):
    queryset = NotificationDeliveryLog.objects.select_related("message", "message__tenant")
    serializer_class = NotificationDeliveryLogSerializer
    permission_classes = [IsTenantAdminOrPlatformAdmin, HasTenantFeature]
    feature_code = TenantFeature.Code.NOTIFICATIONS

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_platform_admin:
            return queryset
        return queryset.filter(message__tenant_id=self.request.user.tenant_id)
