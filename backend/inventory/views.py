from decimal import Decimal

from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet

from accounts.permissions import IsTenantAdminOrPlatformAdmin
from .models import InventoryItem, InventoryTransaction
from .serializers import InventoryItemSerializer, InventoryTransactionSerializer


class TenantScopedInventoryViewSet(ModelViewSet):
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


class InventoryItemViewSet(TenantScopedInventoryViewSet):
    queryset = InventoryItem.objects.select_related("tenant", "branch")
    serializer_class = InventoryItemSerializer

    def perform_create(self, serializer):
        tenant = self.current_tenant()
        branch = serializer.validated_data["branch"]
        if branch.tenant_id != tenant.id:
            raise ValidationError({"branch": "Branch must belong to the current tenant."})
        serializer.save(tenant=tenant)


class InventoryTransactionViewSet(TenantScopedInventoryViewSet):
    queryset = InventoryTransaction.objects.select_related("tenant", "item", "case", "created_by")
    serializer_class = InventoryTransactionSerializer

    def perform_create(self, serializer):
        tenant = self.current_tenant()
        item = serializer.validated_data["item"]
        case = serializer.validated_data.get("case")
        quantity = Decimal(str(serializer.validated_data["quantity"]))
        transaction_type = serializer.validated_data["transaction_type"]
        if item.tenant_id != tenant.id:
            raise ValidationError({"item": "Inventory item must belong to the current tenant."})
        if case and case.tenant_id != tenant.id:
            raise ValidationError({"case": "Case must belong to the current tenant."})
        if transaction_type == InventoryTransaction.TransactionType.STOCK_OUT and item.quantity_on_hand < quantity:
            raise ValidationError({"quantity": "Insufficient stock on hand."})
        serializer.save(tenant=tenant, created_by=self.request.user)
