from rest_framework import serializers

from .models import CalendarEvent, Resource


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ["id", "tenant", "branch", "name", "resource_type", "is_active"]
        read_only_fields = ["id", "tenant"]


class CalendarEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarEvent
        fields = [
            "id",
            "tenant",
            "branch",
            "case",
            "title",
            "event_type",
            "starts_at",
            "ends_at",
            "location",
            "resources",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["id", "tenant", "created_by", "created_at"]
