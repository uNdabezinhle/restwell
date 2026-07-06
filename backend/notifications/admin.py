from django.contrib import admin

from .models import NotificationDeliveryLog, NotificationMessage, NotificationTemplate


class NotificationDeliveryLogInline(admin.TabularInline):
    model = NotificationDeliveryLog
    extra = 0


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ["code", "tenant", "channel", "is_active", "updated_at"]
    list_filter = ["channel", "is_active"]
    search_fields = ["code", "subject", "body", "tenant__name"]


@admin.register(NotificationMessage)
class NotificationMessageAdmin(admin.ModelAdmin):
    list_display = ["channel", "tenant", "recipient_name", "recipient_email", "status", "created_at", "sent_at"]
    list_filter = ["channel", "status"]
    search_fields = ["recipient_name", "recipient_email", "recipient_phone", "subject", "body"]
    inlines = [NotificationDeliveryLogInline]


@admin.register(NotificationDeliveryLog)
class NotificationDeliveryLogAdmin(admin.ModelAdmin):
    list_display = ["message", "provider", "status", "created_at"]
    list_filter = ["provider", "status"]
