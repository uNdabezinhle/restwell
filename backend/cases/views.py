from django.db import transaction
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts.permissions import IsTenantOperationsUser
from platform_core.models import AuditLog
from platform_core.services import write_audit_log
from tenants.models import Branch
from .models import Case, CaseDocument, Deceased, FamilyMember
from .serializers import CaseDocumentSerializer, CaseSerializer, DeceasedSerializer, FamilyMemberSerializer


class TenantScopedViewSet(ModelViewSet):
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

    @action(detail=True, methods=["post"], url_path="advance-status")
    def advance_status(self, request, pk=None):
        case = self.get_object()
        next_status = request.data.get("status")
        valid_statuses = {choice[0] for choice in Case.Status.choices}
        if next_status not in valid_statuses:
            raise ValidationError({"status": "Choose a valid case status."})
        case.status = next_status
        case.save(update_fields=["status", "updated_at"])
        write_audit_log(
            action=AuditLog.Action.WORKFLOW,
            resource=case,
            actor=request.user,
            description=f"Case status advanced to {next_status}.",
            metadata={"status": next_status},
        )
        return Response(self.get_serializer(case).data)

    @action(detail=False, methods=["post"], url_path="intake")
    def intake(self, request):
        tenant = self.get_tenant()
        branch_id = request.data.get("branch")
        reference = request.data.get("reference")
        deceased_data = request.data.get("deceased") or {}
        family_data = request.data.get("family_member") or {}

        if not branch_id:
            raise ValidationError({"branch": "Branch is required."})
        if not reference:
            raise ValidationError({"reference": "Case reference is required."})
        if not deceased_data.get("first_name") or not deceased_data.get("last_name"):
            raise ValidationError({"deceased": "Deceased first and last name are required."})
        status = request.data.get("status") or Case.Status.NEW
        if status not in {choice[0] for choice in Case.Status.choices}:
            raise ValidationError({"status": "Choose a valid case status."})

        try:
            branch = tenant.branches.get(id=branch_id)
        except Branch.DoesNotExist:
            raise ValidationError({"branch": "Branch must belong to the current tenant."})

        with transaction.atomic():
            deceased = Deceased.objects.create(
                tenant=tenant,
                branch=branch,
                first_name=deceased_data["first_name"],
                last_name=deceased_data["last_name"],
                id_number=deceased_data.get("id_number", ""),
                date_of_birth=deceased_data.get("date_of_birth") or None,
                date_of_death=deceased_data.get("date_of_death") or None,
                place_of_death=deceased_data.get("place_of_death", ""),
            )
            case = Case.objects.create(
                tenant=tenant,
                branch=branch,
                deceased=deceased,
                reference=reference,
                status=status,
                service_date=request.data.get("service_date") or None,
                notes=request.data.get("notes", ""),
                created_by=request.user,
            )
            if family_data.get("first_name") and family_data.get("last_name"):
                FamilyMember.objects.create(
                    tenant=tenant,
                    case=case,
                    first_name=family_data["first_name"],
                    last_name=family_data["last_name"],
                    relationship=family_data.get("relationship", "Family"),
                    phone=family_data.get("phone", ""),
                    email=family_data.get("email", ""),
                    is_next_of_kin=family_data.get("is_next_of_kin", True),
                )
            write_audit_log(
                action=AuditLog.Action.WORKFLOW,
                resource=case,
                actor=request.user,
                description=f"Case intake completed for {case.reference}.",
                metadata={"deceased": deceased.id, "branch": branch.id},
            )
        return Response(self.get_serializer(case).data, status=201)


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
