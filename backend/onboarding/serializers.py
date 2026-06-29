from rest_framework import serializers

from .models import HelpArticle, OnboardingTask, TenantOnboardingStatus


class TenantOnboardingStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantOnboardingStatus
        fields = ["id", "tenant", "status", "current_step", "started_at", "completed_at", "updated_at"]
        read_only_fields = ["id", "tenant", "updated_at"]


class OnboardingTaskSerializer(serializers.ModelSerializer):
    is_completed = serializers.BooleanField(read_only=True)

    class Meta:
        model = OnboardingTask
        fields = [
            "id",
            "tenant",
            "title",
            "description",
            "category",
            "is_required",
            "sort_order",
            "completed_by",
            "completed_at",
            "created_at",
            "is_completed",
        ]
        read_only_fields = ["id", "tenant", "completed_by", "completed_at", "created_at", "is_completed"]


class HelpArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = HelpArticle
        fields = [
            "id",
            "tenant",
            "slug",
            "title",
            "summary",
            "body",
            "category",
            "audience",
            "is_published",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "tenant", "created_at", "updated_at"]
