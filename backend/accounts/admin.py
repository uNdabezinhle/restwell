from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class RestWellUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("RestWell access", {"fields": ("tenant", "branch", "role")}),
    )
    list_display = ("username", "email", "role", "tenant", "branch", "is_staff", "is_active")
    list_filter = UserAdmin.list_filter + ("role", "tenant")
