from rest_framework import serializers

from .models import AuditLog, ConsentRecord, DataSubjectRequest, TenantFeature


class TenantFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantFeature
        fields = ["id", "tenant", "code", "is_enabled", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class AuditLogSerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source="actor.username", read_only=True)

    class Meta:
        model = AuditLog
        fields = ["id", "tenant", "actor", "actor_username", "action", "resource_type", "resource_id", "description", "metadata", "created_at"]
        read_only_fields = fields


class ConsentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsentRecord
        fields = ["id", "tenant", "subject_name", "subject_email", "purpose", "granted", "source", "recorded_by", "recorded_at"]
        read_only_fields = ["id", "tenant", "recorded_by", "recorded_at"]


class DataSubjectRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSubjectRequest
        fields = ["id", "tenant", "request_type", "status", "subject_name", "subject_email", "notes", "assigned_to", "created_at", "completed_at"]
        read_only_fields = ["id", "tenant", "created_at"]
