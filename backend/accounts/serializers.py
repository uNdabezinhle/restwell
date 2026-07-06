from rest_framework import serializers

from .models import User


class CurrentUserSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source="tenant.name", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "role", "tenant", "tenant_name", "branch", "branch_name"]
        read_only_fields = fields


class UserSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source="tenant.name", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=False)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "tenant",
            "tenant_name",
            "branch",
            "branch_name",
            "is_active",
            "password",
        ]
        read_only_fields = ["id", "tenant_name", "branch_name"]

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
