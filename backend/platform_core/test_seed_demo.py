from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from accounts.models import User
from cases.models import Case, FamilyMember
from client_portal.models import ClientSupportRequest
from financials.models import Invoice
from notifications.models import NotificationMessage
from platform_core.models import TenantFeature
from tenants.models import Tenant
from website_builder.models import WebsiteBlock, WebsitePage


class SeedDemoCommandTests(TestCase):
    def test_seed_demo_creates_visible_demo_workspace(self):
        output = StringIO()

        call_command("seed_demo", stdout=output)

        tenant = Tenant.objects.get(slug="restwell-demo")
        self.assertTrue(User.objects.filter(username="admin@restwell.local", tenant=tenant).exists())
        self.assertTrue(User.objects.filter(username="family@restwell.local", tenant=tenant).exists())
        self.assertGreaterEqual(TenantFeature.objects.filter(tenant=tenant, is_enabled=True).count(), 5)
        self.assertTrue(Case.objects.filter(tenant=tenant).exists())
        self.assertTrue(FamilyMember.objects.filter(tenant=tenant, email="family@example.com").exists())
        self.assertTrue(Invoice.objects.filter(tenant=tenant).exists())
        self.assertTrue(WebsitePage.objects.filter(tenant=tenant, slug="home").exists())
        self.assertTrue(WebsiteBlock.objects.filter(tenant=tenant).exists())
        self.assertTrue(NotificationMessage.objects.filter(tenant=tenant).exists())
        self.assertEqual(ClientSupportRequest.objects.filter(tenant=tenant).count(), 0)
        self.assertIn("Seeded RestWell demo tenant", output.getvalue())
