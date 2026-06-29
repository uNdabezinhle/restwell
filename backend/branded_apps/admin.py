from django.contrib import admin

from .models import AppBuildRequest, TenantAppConfig


class AppBuildRequestInline(admin.TabularInline):
    model = AppBuildRequest
    extra = 0


@admin.register(TenantAppConfig)
class TenantAppConfigAdmin(admin.ModelAdmin):
    list_display = ["app_name", "tenant", "package_name", "version_name", "version_code", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["app_name", "package_name", "tenant__name", "tenant__slug"]
    inlines = [AppBuildRequestInline]


@admin.register(AppBuildRequest)
class AppBuildRequestAdmin(admin.ModelAdmin):
    list_display = ["app_config", "tenant", "platform", "status", "requested_by", "requested_at"]
    list_filter = ["platform", "status"]
    search_fields = ["app_config__app_name", "tenant__name", "requested_by__username"]
