from django.contrib import admin

from .models import InventoryItem, InventoryTransaction


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "branch", "sku", "quantity_on_hand", "reorder_level", "is_active")
    list_filter = ("tenant", "branch", "category", "is_active")
    search_fields = ("name", "sku")


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ("item", "tenant", "transaction_type", "quantity", "case", "created_by", "created_at")
    list_filter = ("tenant", "transaction_type")
    search_fields = ("item__name", "item__sku", "case__reference")
