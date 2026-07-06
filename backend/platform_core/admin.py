from django.contrib import admin

from .models import AuditLog, ConsentRecord, DataSubjectRequest, TenantFeature


@admin.register(TenantFeature)
class TenantFeatureAdmin(admin.ModelAdmin):
    list_display = ["tenant", "code", "is_enabled", "updated_at"]
    list_filter = ["code", "is_enabled"]
    search_fields = ["tenant__name", "tenant__slug", "code"]


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["action", "resource_type", "resource_id", "tenant", "actor", "created_at"]
    list_filter = ["action", "tenant"]
    search_fields = ["resource_type", "resource_id", "description", "actor__username"]
    readonly_fields = ["tenant", "actor", "action", "resource_type", "resource_id", "description", "metadata", "created_at"]


@admin.register(ConsentRecord)
class ConsentRecordAdmin(admin.ModelAdmin):
    list_display = ["subject_name", "tenant", "purpose", "granted", "recorded_at"]
    list_filter = ["granted", "purpose"]
    search_fields = ["subject_name", "subject_email", "purpose"]


@admin.register(DataSubjectRequest)
class DataSubjectRequestAdmin(admin.ModelAdmin):
    list_display = ["subject_name", "tenant", "request_type", "status", "created_at"]
    list_filter = ["request_type", "status"]
    search_fields = ["subject_name", "subject_email", "notes"]
