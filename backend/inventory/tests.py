from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from cases.models import Case, Deceased
from inventory.models import InventoryItem, InventoryTransaction
from tenants.models import Branch, Tenant


class InventoryApiTests(APITestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="RestWell Demo", slug="restwell-demo")
        self.branch = Branch.objects.create(tenant=self.tenant, name="Johannesburg", code="JHB")
        self.other_tenant = Tenant.objects.create(name="Other Care", slug="other-care")
        self.other_branch = Branch.objects.create(tenant=self.other_tenant, name="Cape Town", code="CPT")
        self.user = User.objects.create_user(
            username="inventory-admin",
            password="test-password",
            tenant=self.tenant,
            branch=self.branch,
            role=User.Role.TENANT_ADMIN,
        )
        deceased = Deceased.objects.create(tenant=self.tenant, branch=self.branch, first_name="Thabo", last_name="Mokoena")
        self.case = Case.objects.create(tenant=self.tenant, branch=self.branch, deceased=deceased, reference="CASE-001")

    def authenticate(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "inventory-admin", "password": "test-password"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def create_item(self, tenant=None, branch=None, sku="CASKET-001"):
        return InventoryItem.objects.create(
            tenant=tenant or self.tenant,
            branch=branch or self.branch,
            name="Standard Casket",
            sku=sku,
            quantity_on_hand="5.00",
            reorder_level="2.00",
            unit_cost="1200.00",
        )

    def test_creates_inventory_item_for_current_tenant(self):
        self.authenticate()

        response = self.client.post(
            reverse("inventoryitem-list"),
            {
                "branch": self.branch.id,
                "name": "Standard Casket",
                "sku": "CASKET-100",
                "category": "Caskets",
                "reorder_level": "2.00",
                "unit_cost": "1200.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["tenant"], self.tenant.id)

    def test_stock_out_deducts_inventory_and_flags_low_stock(self):
        self.authenticate()
        item = self.create_item()

        response = self.client.post(
            reverse("inventorytransaction-list"),
            {
                "item": item.id,
                "case": self.case.id,
                "transaction_type": InventoryTransaction.TransactionType.STOCK_OUT,
                "quantity": "4.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        item.refresh_from_db()
        self.assertEqual(item.quantity_on_hand, Decimal("1.00"))
        self.assertTrue(item.is_low_stock)

    def test_rejects_stock_out_above_available_quantity(self):
        self.authenticate()
        item = self.create_item()

        response = self.client.post(
            reverse("inventorytransaction-list"),
            {
                "item": item.id,
                "transaction_type": InventoryTransaction.TransactionType.STOCK_OUT,
                "quantity": "6.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_tenant_user_only_sees_own_inventory(self):
        own_item = self.create_item()
        other_item = self.create_item(tenant=self.other_tenant, branch=self.other_branch, sku="OTHER-001")
        self.authenticate()

        response = self.client.get(reverse("inventoryitem-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item_ids = {item["id"] for item in response.data}
        self.assertEqual(item_ids, {own_item.id})
        self.assertNotIn(other_item.id, item_ids)
