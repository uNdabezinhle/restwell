from decimal import Decimal

from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts.permissions import IsTenantOperationsUser
from platform_core.models import AuditLog
from platform_core.services import write_audit_log
from .models import InventoryItem, InventoryTransaction
from .serializers import InventoryItemSerializer, InventoryTransactionSerializer


class TenantScopedInventoryViewSet(ModelViewSet):
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


class InventoryItemViewSet(TenantScopedInventoryViewSet):
    queryset = InventoryItem.objects.select_related("tenant", "branch")
    serializer_class = InventoryItemSerializer

    def perform_create(self, serializer):
        tenant = self.current_tenant()
        branch = serializer.validated_data["branch"]
        if branch.tenant_id != tenant.id:
            raise ValidationError({"branch": "Branch must belong to the current tenant."})
        serializer.save(tenant=tenant)

    @action(detail=True, methods=["post"], url_path="adjust-stock")
    def adjust_stock(self, request, pk=None):
        item = self.get_object()
        quantity = Decimal(str(request.data.get("quantity", "0")))
        transaction_type = request.data.get("transaction_type", InventoryTransaction.TransactionType.ADJUSTMENT)
        if transaction_type not in {choice[0] for choice in InventoryTransaction.TransactionType.choices}:
            raise ValidationError({"transaction_type": "Choose a valid transaction type."})
        if quantity <= 0:
            raise ValidationError({"quantity": "Quantity must be greater than zero."})
        if transaction_type == InventoryTransaction.TransactionType.STOCK_OUT and item.quantity_on_hand < quantity:
            raise ValidationError({"quantity": "Insufficient stock on hand."})
        transaction = InventoryTransaction.objects.create(
            tenant=item.tenant,
            item=item,
            transaction_type=transaction_type,
            quantity=quantity,
            note=request.data.get("note", ""),
            created_by=request.user,
        )
        write_audit_log(
            action=AuditLog.Action.WORKFLOW,
            resource=transaction,
            actor=request.user,
            description=f"Inventory {transaction_type} recorded for {item.name}.",
            metadata={"item": item.id, "quantity": str(quantity)},
        )
        item.refresh_from_db()
        return Response(self.get_serializer(item).data)


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
