from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts.permissions import IsTenantOperationsUser
from platform_core.models import AuditLog, TenantFeature
from platform_core.permissions import HasTenantFeature
from platform_core.services import write_audit_log
from .models import MortuaryRecord, PreparationTask
from .serializers import MortuaryRecordSerializer, PreparationTaskSerializer


class TenantScopedMortuaryViewSet(ModelViewSet):
    permission_classes = [IsTenantOperationsUser, HasTenantFeature]
    feature_code = TenantFeature.Code.MORTUARY
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


class MortuaryRecordViewSet(TenantScopedMortuaryViewSet):
    queryset = MortuaryRecord.objects.select_related("tenant", "branch", "case", "deceased", "created_by").prefetch_related(
        "preparation_tasks"
    )
    serializer_class = MortuaryRecordSerializer

    def perform_create(self, serializer):
        tenant = self.current_tenant()
        branch = serializer.validated_data["branch"]
        deceased = serializer.validated_data["deceased"]
        case = serializer.validated_data.get("case")
        if branch.tenant_id != tenant.id:
            raise ValidationError({"branch": "Branch must belong to the current tenant."})
        if deceased.tenant_id != tenant.id:
            raise ValidationError({"deceased": "Deceased record must belong to the current tenant."})
        if case and case.tenant_id != tenant.id:
            raise ValidationError({"case": "Case must belong to the current tenant."})
        serializer.save(tenant=tenant, created_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="release")
    def release(self, request, pk=None):
        record = self.get_object()
        record.status = MortuaryRecord.Status.RELEASED
        record.released_at = timezone.now()
        record.save(update_fields=["status", "released_at", "updated_at"])
        write_audit_log(
            action=AuditLog.Action.WORKFLOW,
            resource=record,
            actor=request.user,
            description="Mortuary record released.",
        )
        return Response(self.get_serializer(record).data)


class PreparationTaskViewSet(TenantScopedMortuaryViewSet):
    queryset = PreparationTask.objects.select_related("tenant", "mortuary_record", "assigned_to")
    serializer_class = PreparationTaskSerializer

    def perform_create(self, serializer):
        tenant = self.current_tenant()
        record = serializer.validated_data["mortuary_record"]
        assigned_to = serializer.validated_data.get("assigned_to")
        if record.tenant_id != tenant.id:
            raise ValidationError({"mortuary_record": "Mortuary record must belong to the current tenant."})
        if assigned_to and assigned_to.tenant_id != tenant.id:
            raise ValidationError({"assigned_to": "Assigned user must belong to the current tenant."})
        serializer.save(tenant=tenant)
