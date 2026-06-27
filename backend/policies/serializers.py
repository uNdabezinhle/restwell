from rest_framework import serializers

from .models import PolicyEnrollment, PolicyTemplate, PremiumPayment, Underwriter


class UnderwriterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Underwriter
        fields = ["id", "tenant", "name", "registration_number", "contact_email", "contact_phone", "is_active"]
        read_only_fields = ["id", "tenant"]


class PolicyTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyTemplate
        fields = [
            "id",
            "tenant",
            "underwriter",
            "name",
            "description",
            "cover_amount",
            "premium_amount",
            "billing_frequency",
            "is_active",
        ]
        read_only_fields = ["id", "tenant"]


class PolicyEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyEnrollment
        fields = [
            "id",
            "tenant",
            "policy_template",
            "underwriter",
            "family_member",
            "policy_number",
            "status",
            "start_date",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["id", "tenant", "underwriter", "created_by", "created_at"]


class PremiumPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PremiumPayment
        fields = ["id", "tenant", "enrollment", "amount", "due_date", "paid_at", "status", "reference", "created_at"]
        read_only_fields = ["id", "tenant", "created_at"]
