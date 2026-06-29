import re

from rest_framework import serializers

from .models import TenantBranding


HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


class TenantBrandingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantBranding
        fields = [
            "id",
            "tenant",
            "logo",
            "primary_color",
            "secondary_color",
            "email_from_name",
            "sms_sender_name",
            "custom_domain",
            "remove_powered_by",
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
