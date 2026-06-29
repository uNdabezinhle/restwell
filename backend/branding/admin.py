from django.contrib import admin

from .models import TenantBranding


@admin.register(TenantBranding)
class TenantBrandingAdmin(admin.ModelAdmin):
    list_display = ["tenant", "primary_color", "secondary_color", "custom_domain", "is_active"]
    list_filter = ["is_active", "remove_powered_by"]
    search_fields = ["tenant__name", "tenant__slug", "custom_domain"]
