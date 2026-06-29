from rest_framework import serializers

from .models import InventoryItem, InventoryTransaction


class InventoryItemSerializer(serializers.ModelSerializer):
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = InventoryItem
        fields = [
            "id",
            "tenant",
            "branch",
            "name",
            "sku",
            "category",
            "quantity_on_hand",
            "reorder_level",
            "unit_cost",
            "is_active",
            "is_low_stock",
        ]
        read_only_fields = ["id", "tenant", "quantity_on_hand", "is_low_stock"]


class InventoryTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryTransaction
        fields = ["id", "tenant", "item", "case", "transaction_type", "quantity", "note", "created_by", "created_at"]
        read_only_fields = ["id", "tenant", "created_by", "created_at"]
