from decimal import Decimal

from django.conf import settings
from django.db import models


class InventoryItem(models.Model):
    tenant = models.ForeignKey("tenants.Tenant", related_name="inventory_items", on_delete=models.CASCADE)
    branch = models.ForeignKey("tenants.Branch", related_name="inventory_items", on_delete=models.PROTECT)
    name = models.CharField(max_length=180)
    sku = models.CharField(max_length=80, blank=True)
    category = models.CharField(max_length=100, blank=True)
    quantity_on_hand = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    reorder_level = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["tenant", "branch", "sku"], name="unique_inventory_sku_per_branch"),
        ]

    @property
    def is_low_stock(self):
        return self.quantity_on_hand <= self.reorder_level

    def __str__(self):
        return self.name


class InventoryTransaction(models.Model):
    class TransactionType(models.TextChoices):
        STOCK_IN = "stock_in", "Stock In"
        STOCK_OUT = "stock_out", "Stock Out"
        ADJUSTMENT = "adjustment", "Adjustment"

    tenant = models.ForeignKey("tenants.Tenant", related_name="inventory_transactions", on_delete=models.CASCADE)
    item = models.ForeignKey(InventoryItem, related_name="transactions", on_delete=models.PROTECT)
    case = models.ForeignKey("cases.Case", related_name="inventory_transactions", null=True, blank=True, on_delete=models.PROTECT)
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.CharField(max_length=220, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            quantity = Decimal(str(self.quantity))
            if self.transaction_type == self.TransactionType.STOCK_OUT:
                self.item.quantity_on_hand -= quantity
            else:
                self.item.quantity_on_hand += quantity
            self.item.save(update_fields=["quantity_on_hand", "updated_at"])

    def __str__(self):
        return f"{self.item} {self.transaction_type} {self.quantity}"
