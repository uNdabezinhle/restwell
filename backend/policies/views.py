from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet

from accounts.permissions import IsTenantOperationsUser
from .models import PolicyEnrollment, PolicyTemplate, PremiumPayment, Underwriter
from .serializers import PolicyEnrollmentSerializer, PolicyTemplateSerializer, PremiumPaymentSerializer, UnderwriterSerializer


class TenantScopedPolicyViewSet(ModelViewSet):
    permission_classes = [IsTenantOperationsUser]
    tenant_field = "tenant_id"

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_platform_admin:
            return queryset
        if user.tenant_id:
            return queryset.filter(**{self.tenant_field: user.tenant_id})
        return queryset.none()

    def current_tenant(self):
        if not self.request.user.tenant_id:
            raise ValidationError("A tenant-scoped user is required.")
        return self.request.user.tenant


class UnderwriterViewSet(TenantScopedPolicyViewSet):
    queryset = Underwriter.objects.select_related("tenant")
    serializer_class = UnderwriterSerializer

    def perform_create(self, serializer):
        serializer.save(tenant=self.current_tenant())


class PolicyTemplateViewSet(TenantScopedPolicyViewSet):
    queryset = PolicyTemplate.objects.select_related("tenant", "underwriter")
    serializer_class = PolicyTemplateSerializer

    def perform_create(self, serializer):
        tenant = self.current_tenant()
        underwriter = serializer.validated_data["underwriter"]
        if underwriter.tenant_id != tenant.id:
            raise ValidationError({"underwriter": "Underwriter must belong to the current tenant."})
        serializer.save(tenant=tenant)


class PolicyEnrollmentViewSet(TenantScopedPolicyViewSet):
    queryset = PolicyEnrollment.objects.select_related("tenant", "policy_template", "underwriter", "family_member")
    serializer_class = PolicyEnrollmentSerializer

    def perform_create(self, serializer):
        tenant = self.current_tenant()
        policy_template = serializer.validated_data["policy_template"]
        family_member = serializer.validated_data["family_member"]
        if policy_template.tenant_id != tenant.id:
            raise ValidationError({"policy_template": "Policy template must belong to the current tenant."})
        if family_member.tenant_id != tenant.id:
            raise ValidationError({"family_member": "Family member must belong to the current tenant."})
        serializer.save(
            tenant=tenant,
            underwriter=policy_template.underwriter,
            created_by=self.request.user,
        )


class PremiumPaymentViewSet(TenantScopedPolicyViewSet):
    queryset = PremiumPayment.objects.select_related("tenant", "enrollment")
    serializer_class = PremiumPaymentSerializer

    def perform_create(self, serializer):
        tenant = self.current_tenant()
        enrollment = serializer.validated_data["enrollment"]
        if enrollment.tenant_id != tenant.id:
            raise ValidationError({"enrollment": "Enrollment must belong to the current tenant."})
        serializer.save(tenant=tenant)
