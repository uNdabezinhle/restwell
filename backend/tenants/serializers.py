from rest_framework import serializers

from .models import Branch, Tenant


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ["id", "tenant", "name", "code", "province", "city", "is_active"]
        read_only_fields = ["id"]


class TenantSerializer(serializers.ModelSerializer):
    branches = BranchSerializer(many=True, read_only=True)

    class Meta:
        model = Tenant
        fields = ["id", "name", "slug", "legal_name", "registration_number", "is_active", "branches"]
        read_only_fields = ["id"]
