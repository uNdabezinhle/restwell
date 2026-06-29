import re

from rest_framework import serializers

from .models import AppBuildRequest, TenantAppConfig


HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
PACKAGE_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$")


class TenantAppConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantAppConfig
        fields = [
            "id",
            "tenant",
            "app_name",
            "package_name",
            "primary_color",
            "secondary_color",
            "logo",
            "support_email",
            "privacy_policy_url",
            "version_name",
            "version_code",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "tenant", "created_at", "updated_at"]

    def validate_primary_color(self, value):
        return self.validate_hex_color(value)

    def validate_secondary_color(self, value):
        return self.validate_hex_color(value)

    def validate_hex_color(self, value):
        if not HEX_COLOR_RE.match(value):
            raise serializers.ValidationError("Use a hex color in #RRGGBB format.")
        return value.upper()

    def validate_package_name(self, value):
        if not PACKAGE_NAME_RE.match(value):
            raise serializers.ValidationError("Use a reverse-DNS Android package name, for example za.co.restwell.demo.")
        return value


class AppBuildRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppBuildRequest
        fields = [
            "id",
            "tenant",
            "app_config",
            "platform",
            "status",
            "requested_by",
            "git_ref",
            "workflow_run_url",
            "artifact_url",
            "error_message",
            "requested_at",
            "completed_at",
        ]
        read_only_fields = [
            "id",
            "tenant",
            "status",
            "requested_by",
            "workflow_run_url",
            "artifact_url",
            "error_message",
            "requested_at",
            "completed_at",
        ]
