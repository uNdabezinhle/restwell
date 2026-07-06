from rest_framework import serializers

from .models import ClientSupportRequest


class ClientSupportRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientSupportRequest
        fields = ["id", "tenant", "family_member", "created_by", "subject", "message", "status", "created_at", "updated_at"]
        read_only_fields = ["id", "tenant", "family_member", "created_by", "status", "created_at", "updated_at"]
