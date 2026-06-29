from rest_framework import serializers

from .models import LocationLog, LocationRoute


class LocationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationLog
        fields = [
            "id",
            "tenant",
            "route",
            "user",
            "case",
            "latitude",
            "longitude",
            "accuracy_meters",
            "recorded_at",
            "note",
            "created_at",
        ]
        read_only_fields = ["id", "tenant", "created_at"]


class LocationRouteSerializer(serializers.ModelSerializer):
    latest_log = serializers.SerializerMethodField()

    class Meta:
        model = LocationRoute
        fields = [
            "id",
            "tenant",
            "branch",
            "case",
            "name",
            "assigned_to",
            "status",
            "origin",
            "destination",
            "started_at",
            "ended_at",
            "created_at",
            "latest_log",
        ]
        read_only_fields = ["id", "tenant", "created_at", "latest_log"]

    def get_latest_log(self, obj):
        latest = obj.logs.order_by("-recorded_at").first()
        if not latest:
            return None
        return LocationLogSerializer(latest).data
