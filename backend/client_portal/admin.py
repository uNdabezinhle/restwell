from django.contrib import admin

from .models import ClientSupportRequest


@admin.register(ClientSupportRequest)
class ClientSupportRequestAdmin(admin.ModelAdmin):
    list_display = ["subject", "tenant", "family_member", "status", "created_at"]
    list_filter = ["status", "tenant"]
    search_fields = ["subject", "message", "family_member__first_name", "family_member__last_name"]
