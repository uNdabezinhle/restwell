# Generated for RestWell Sprint 4 inventory.

import django.db.models.deletion
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("cases", "0001_initial"),
        ("tenants", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="InventoryItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=180)),
                ("sku", models.CharField(blank=True, max_length=80)),
                ("category", models.CharField(blank=True, max_length=100)),
                ("quantity_on_hand", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("reorder_level", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("unit_cost", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("branch", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="inventory_items", to="tenants.branch")),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="inventory_items", to="tenants.tenant")),
            ],
            options={
                "ordering": ["name"],
                "constraints": [models.UniqueConstraint(fields=("tenant", "branch", "sku"), name="unique_inventory_sku_per_branch")],
            },
        ),
        migrations.CreateModel(
            name="InventoryTransaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("transaction_type", models.CharField(choices=[("stock_in", "Stock In"), ("stock_out", "Stock Out"), ("adjustment", "Adjustment")], max_length=20)),
                ("quantity", models.DecimalField(decimal_places=2, max_digits=12)),
                ("note", models.CharField(blank=True, max_length=220)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("case", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="inventory_transactions", to="cases.case")),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ("item", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="transactions", to="inventory.inventoryitem")),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="inventory_transactions", to="tenants.tenant")),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
