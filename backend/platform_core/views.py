from django.db.models import Sum
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from accounts.permissions import IsTenantAdminOrPlatformAdmin, IsTenantOperationsUser
from branded_apps.models import AppBuildRequest, TenantAppConfig
from branding.models import TenantBranding
from cases.models import Case, Deceased, FamilyMember
from financials.models import DebtorAccount, Invoice, Payment
from geolocation.models import LocationRoute
from inventory.models import InventoryItem
from mortuary.models import MortuaryRecord
from onboarding.models import OnboardingTask
from policies.models import PolicyEnrollment, PolicyTemplate
from scheduling.models import CalendarEvent
from website_builder.models import WebsitePage, WebsiteSite
from .models import AuditLog, ConsentRecord, DataSubjectRequest, TenantFeature
from .serializers import AuditLogSerializer, ConsentRecordSerializer, DataSubjectRequestSerializer, TenantFeatureSerializer


class TenantScopedPlatformViewSet(ModelViewSet):
    permission_classes = [IsTenantAdminOrPlatformAdmin]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_platform_admin:
            return queryset
        if user.tenant_id:
            return queryset.filter(tenant_id=user.tenant_id)
        return queryset.none()

    def current_tenant(self):
        if not self.request.user.tenant_id:
            raise ValidationError("A tenant-scoped user is required.")
        return self.request.user.tenant


class TenantFeatureViewSet(TenantScopedPlatformViewSet):
    queryset = TenantFeature.objects.select_related("tenant")
    serializer_class = TenantFeatureSerializer

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [IsTenantOperationsUser()]
        return [IsTenantAdminOrPlatformAdmin()]

    def perform_create(self, serializer):
        tenant = serializer.validated_data.get("tenant") if self.request.user.is_platform_admin else self.current_tenant()
        serializer.save(tenant=tenant)


class AuditLogViewSet(ReadOnlyModelViewSet):
    queryset = AuditLog.objects.select_related("tenant", "actor")
    serializer_class = AuditLogSerializer
    permission_classes = [IsTenantAdminOrPlatformAdmin]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_platform_admin:
            return queryset
        return queryset.filter(tenant_id=user.tenant_id)


class ConsentRecordViewSet(TenantScopedPlatformViewSet):
    queryset = ConsentRecord.objects.select_related("tenant", "recorded_by")
    serializer_class = ConsentRecordSerializer

    def perform_create(self, serializer):
        serializer.save(tenant=self.current_tenant(), recorded_by=self.request.user)


class DataSubjectRequestViewSet(TenantScopedPlatformViewSet):
    queryset = DataSubjectRequest.objects.select_related("tenant", "assigned_to")
    serializer_class = DataSubjectRequestSerializer

    def perform_create(self, serializer):
        serializer.save(tenant=self.current_tenant())


@api_view(["GET"])
@permission_classes([IsTenantOperationsUser])
def dashboard_summary(request):
    tenant_id = None if request.user.is_platform_admin else request.user.tenant_id

    def scoped(model):
        queryset = model.objects.all()
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        return queryset

    payments = scoped(Payment).filter(status=Payment.Status.COMPLETED)
    debtors = scoped(DebtorAccount).filter(status=DebtorAccount.Status.OPEN)
    return Response(
        {
            "operations": {
                "cases": scoped(Case).count(),
                "deceased": scoped(Deceased).count(),
                "family_members": scoped(FamilyMember).count(),
                "mortuary_records": scoped(MortuaryRecord).count(),
                "scheduled_events": scoped(CalendarEvent).count(),
                "active_routes": scoped(LocationRoute).filter(status=LocationRoute.Status.ACTIVE).count(),
            },
            "commercial": {
                "policy_templates": scoped(PolicyTemplate).count(),
                "policy_enrollments": scoped(PolicyEnrollment).count(),
                "invoices": scoped(Invoice).count(),
                "total_paid": payments.aggregate(total=Sum("amount"))["total"] or 0,
                "outstanding_debt": debtors.aggregate(total=Sum("amount_due"))["total"] or 0,
                "inventory_items": scoped(InventoryItem).count(),
            },
            "digital": {
                "branding_profiles": scoped(TenantBranding).count(),
                "website_sites": scoped(WebsiteSite).count(),
                "website_pages": scoped(WebsitePage).count(),
                "app_configs": scoped(TenantAppConfig).count(),
                "app_build_requests": scoped(AppBuildRequest).count(),
                "onboarding_open": scoped(OnboardingTask).filter(completed_at__isnull=True).count(),
            },
        }
    )
