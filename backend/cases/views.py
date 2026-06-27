from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.viewsets import ModelViewSet

from accounts.permissions import IsTenantAdminOrPlatformAdmin
from .models import Case, CaseDocument, Deceased, FamilyMember
from .serializers import CaseDocumentSerializer, CaseSerializer, DeceasedSerializer, FamilyMemberSerializer


class TenantScopedViewSet(ModelViewSet):
    permission_classes = [IsTenantAdminOrPlatformAdmin]
    tenant_field = "tenant_id"

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_platform_admin:
            return queryset
        if user.tenant_id:
            return queryset.filter(**{self.tenant_field: user.tenant_id})
        return queryset.none()

    def get_tenant(self):
        user = self.request.user
        if not user.tenant_id:
            raise PermissionDenied("A tenant-scoped user is required.")
        return user.tenant


class DeceasedViewSet(TenantScopedViewSet):
    queryset = Deceased.objects.select_related("tenant", "branch")
    serializer_class = DeceasedSerializer

    def perform_create(self, serializer):
        tenant = self.get_tenant()
        branch = serializer.validated_data["branch"]
        if branch.tenant_id != tenant.id:
            raise ValidationError({"branch": "Branch must belong to the current tenant."})
        serializer.save(tenant=tenant)


class CaseViewSet(TenantScopedViewSet):
    queryset = Case.objects.select_related("tenant", "branch", "deceased", "created_by").prefetch_related(
        "family_members",
        "documents",
    )
    serializer_class = CaseSerializer

    def perform_create(self, serializer):
        tenant = self.get_tenant()
        branch = serializer.validated_data["branch"]
        deceased = serializer.validated_data["deceased"]
        if branch.tenant_id != tenant.id:
            raise ValidationError({"branch": "Branch must belong to the current tenant."})
        if deceased.tenant_id != tenant.id:
            raise ValidationError({"deceased": "Deceased record must belong to the current tenant."})
        serializer.save(tenant=tenant, created_by=self.request.user)


class FamilyMemberViewSet(TenantScopedViewSet):
    queryset = FamilyMember.objects.select_related("tenant", "case")
    serializer_class = FamilyMemberSerializer

    def perform_create(self, serializer):
        case = serializer.validated_data["case"]
        tenant = self.get_tenant()
        if case.tenant_id != tenant.id:
            raise ValidationError({"case": "Case must belong to the current tenant."})
        serializer.save(tenant=tenant)


class CaseDocumentViewSet(TenantScopedViewSet):
    queryset = CaseDocument.objects.select_related("tenant", "case", "uploaded_by")
    serializer_class = CaseDocumentSerializer

    def perform_create(self, serializer):
        case = serializer.validated_data["case"]
        tenant = self.get_tenant()
        if case.tenant_id != tenant.id:
            raise ValidationError({"case": "Case must belong to the current tenant."})
        serializer.save(tenant=tenant, uploaded_by=self.request.user)
