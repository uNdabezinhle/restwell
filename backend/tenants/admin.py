from django.contrib import admin

from .models import Branch, Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    search_fields = ("name", "slug", "legal_name")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "code", "city", "province", "is_active")
    list_filter = ("tenant", "is_active", "province")
    search_fields = ("name", "code", "city")
