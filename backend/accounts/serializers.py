from rest_framework import serializers

from .models import User


class CurrentUserSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source="tenant.name", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "role", "tenant", "tenant_name", "branch", "branch_name"]
        read_only_fields = fields
