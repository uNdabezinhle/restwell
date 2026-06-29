from django.db.models import Sum
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from accounts.permissions import IsTenantAdminOrPlatformAdmin
from .models import DebtorAccount, Invoice, InvoiceLineItem, Payment
from .serializers import DebtorAccountSerializer, InvoiceLineItemSerializer, InvoiceSerializer, PaymentSerializer


class TenantScopedFinancialViewSet(ModelViewSet):
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

    def current_tenant(self):
        if not self.request.user.tenant_id:
            raise ValidationError("A tenant-scoped user is required.")
        return self.request.user.tenant


class InvoiceViewSet(TenantScopedFinancialViewSet):
    queryset = Invoice.objects.select_related("tenant", "branch", "case", "policy_enrollment", "created_by").prefetch_related(
        "line_items",
        "payments",
    )
    serializer_class = InvoiceSerializer

    def perform_create(self, serializer):
        tenant = self.current_tenant()
        branch = serializer.validated_data["branch"]
        if branch.tenant_id != tenant.id:
            raise ValidationError({"branch": "Branch must belong to the current tenant."})
        case = serializer.validated_data.get("case")
        if case and case.tenant_id != tenant.id:
            raise ValidationError({"case": "Case must belong to the current tenant."})
        enrollment = serializer.validated_data.get("policy_enrollment")
        if enrollment and enrollment.tenant_id != tenant.id:
            raise ValidationError({"policy_enrollment": "Policy enrollment must belong to the current tenant."})
        serializer.save(tenant=tenant, created_by=self.request.user)


class InvoiceLineItemViewSet(TenantScopedFinancialViewSet):
    queryset = InvoiceLineItem.objects.select_related("tenant", "invoice")
    serializer_class = InvoiceLineItemSerializer

    def perform_create(self, serializer):
        tenant = self.current_tenant()
        invoice = serializer.validated_data["invoice"]
        if invoice.tenant_id != tenant.id:
            raise ValidationError({"invoice": "Invoice must belong to the current tenant."})
        serializer.save(tenant=tenant)


class PaymentViewSet(TenantScopedFinancialViewSet):
    queryset = Payment.objects.select_related("tenant", "invoice", "received_by")
    serializer_class = PaymentSerializer

    def perform_create(self, serializer):
        tenant = self.current_tenant()
        invoice = serializer.validated_data["invoice"]
        if invoice.tenant_id != tenant.id:
            raise ValidationError({"invoice": "Invoice must belong to the current tenant."})
        serializer.save(tenant=tenant, received_by=self.request.user)


class DebtorAccountViewSet(ReadOnlyModelViewSet):
    queryset = DebtorAccount.objects.select_related("tenant", "invoice")
    serializer_class = DebtorAccountSerializer
    permission_classes = [IsTenantAdminOrPlatformAdmin]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_platform_admin:
            return queryset
        if user.tenant_id:
            return queryset.filter(tenant_id=user.tenant_id)
        return queryset.none()


@api_view(["GET"])
@permission_classes([IsTenantAdminOrPlatformAdmin])
def financial_summary(request):
    invoices = Invoice.objects.all()
    debtors = DebtorAccount.objects.all()
    payments = Payment.objects.filter(status=Payment.Status.COMPLETED)
    if not request.user.is_platform_admin:
        invoices = invoices.filter(tenant_id=request.user.tenant_id)
        debtors = debtors.filter(tenant_id=request.user.tenant_id)
        payments = payments.filter(tenant_id=request.user.tenant_id)

    return Response(
        {
            "invoice_count": invoices.count(),
            "total_invoiced": invoices.aggregate(total=Sum("total_amount"))["total"] or 0,
            "total_paid": payments.aggregate(total=Sum("amount"))["total"] or 0,
            "outstanding_debt": debtors.filter(status=DebtorAccount.Status.OPEN).aggregate(total=Sum("amount_due"))["total"] or 0,
        }
    )
