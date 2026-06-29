from django.contrib import admin

from .models import LocationLog, LocationRoute


class LocationLogInline(admin.TabularInline):
    model = LocationLog
    extra = 0


@admin.register(LocationRoute)
class LocationRouteAdmin(admin.ModelAdmin):
    list_display = ["name", "tenant", "branch", "assigned_to", "status", "started_at", "ended_at"]
    list_filter = ["status", "branch"]
    search_fields = ["name", "origin", "destination", "assigned_to__username"]
    inlines = [LocationLogInline]


@admin.register(LocationLog)
class LocationLogAdmin(admin.ModelAdmin):
    list_display = ["user", "tenant", "route", "latitude", "longitude", "recorded_at"]
    list_filter = ["tenant", "recorded_at"]
    search_fields = ["user__username", "route__name", "note"]
