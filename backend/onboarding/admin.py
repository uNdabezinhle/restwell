from django.contrib import admin

from .models import HelpArticle, OnboardingTask, TenantOnboardingStatus


@admin.register(TenantOnboardingStatus)
class TenantOnboardingStatusAdmin(admin.ModelAdmin):
    list_display = ["tenant", "status", "current_step", "started_at", "completed_at"]
    list_filter = ["status"]
    search_fields = ["tenant__name", "tenant__slug", "current_step"]


@admin.register(OnboardingTask)
class OnboardingTaskAdmin(admin.ModelAdmin):
    list_display = ["title", "tenant", "category", "is_required", "sort_order", "completed_at"]
    list_filter = ["category", "is_required"]
    search_fields = ["title", "description", "tenant__name"]


@admin.register(HelpArticle)
class HelpArticleAdmin(admin.ModelAdmin):
    list_display = ["title", "tenant", "category", "audience", "is_published"]
    list_filter = ["category", "audience", "is_published"]
    search_fields = ["title", "summary", "body", "tenant__name"]
