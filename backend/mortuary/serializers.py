from rest_framework import serializers

from .models import MortuaryRecord, PreparationTask


class PreparationTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreparationTask
        fields = [
            "id",
            "tenant",
            "mortuary_record",
            "task_type",
            "status",
            "assigned_to",
            "due_at",
            "completed_at",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "tenant", "created_at"]


class MortuaryRecordSerializer(serializers.ModelSerializer):
    preparation_tasks = PreparationTaskSerializer(many=True, read_only=True)

    class Meta:
        model = MortuaryRecord
        fields = [
            "id",
            "tenant",
            "branch",
            "case",
            "deceased",
            "intake_reference",
            "status",
            "storage_location",
            "storage_unit",
            "intake_at",
            "released_at",
            "preparation_notes",
            "created_by",
            "created_at",
            "updated_at",
            "preparation_tasks",
        ]
        read_only_fields = ["id", "tenant", "created_by", "created_at", "updated_at"]
