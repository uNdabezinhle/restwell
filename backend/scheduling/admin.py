from django.contrib import admin

from .models import CalendarEvent, Resource


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "branch", "resource_type", "is_active")
    list_filter = ("tenant", "branch", "resource_type", "is_active")
    search_fields = ("name",)


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ("title", "tenant", "branch", "event_type", "starts_at", "ends_at", "case")
    list_filter = ("tenant", "branch", "event_type")
    search_fields = ("title", "case__reference")
    filter_horizontal = ("resources",)
