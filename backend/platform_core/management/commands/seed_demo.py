from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User
from branding.models import TenantBranding
from cases.models import Case, Deceased, FamilyMember
from financials.models import Invoice, InvoiceLineItem, Payment
from inventory.models import InventoryItem, InventoryTransaction
from mortuary.models import MortuaryRecord, PreparationTask
from notifications.models import NotificationMessage, NotificationTemplate
from notifications.services import send_notification
from onboarding.models import HelpArticle, OnboardingTask
from platform_core.models import ConsentRecord, TenantFeature
from policies.models import PolicyEnrollment, PolicyTemplate, PremiumPayment, Underwriter
from scheduling.models import CalendarEvent, Resource
from tenants.models import Branch, Tenant
from website_builder.models import WebsiteBlock, WebsitePage, WebsiteSite


class Command(BaseCommand):
    help = "Seed a realistic RestWell demo tenant for local development."

    def handle(self, *args, **options):
        tenant, _ = Tenant.objects.get_or_create(
            slug="restwell-demo",
            defaults={"name": "RestWell Demo", "legal_name": "RestWell Demo Pty Ltd", "is_active": True},
        )
        branch, _ = Branch.objects.get_or_create(
            tenant=tenant,
            code="JHB",
            defaults={"name": "Johannesburg", "province": "Gauteng", "city": "Johannesburg", "is_active": True},
        )
        admin, _ = User.objects.get_or_create(
            username="admin@restwell.local",
            defaults={
                "email": "admin@restwell.local",
                "first_name": "RestWell",
                "last_name": "Admin",
                "tenant": tenant,
                "branch": branch,
                "role": User.Role.TENANT_ADMIN,
                "is_staff": True,
            },
        )
        admin.tenant = tenant
        admin.branch = branch
        admin.role = User.Role.TENANT_ADMIN
        admin.is_staff = True
        admin.is_active = True
        admin.set_password("RestWell123!")
        admin.save()

        for code in TenantFeature.Code.values:
            TenantFeature.objects.update_or_create(tenant=tenant, code=code, defaults={"is_enabled": True})

        TenantBranding.objects.get_or_create(
            tenant=tenant,
            defaults={
                "primary_color": "#0F766E",
                "secondary_color": "#2563EB",
                "email_from_name": "RestWell Demo",
                "sms_sender_name": "RESTWELL",
            },
        )

        deceased, _ = Deceased.objects.get_or_create(
            tenant=tenant,
            branch=branch,
            first_name="Thabo",
            last_name="Mokoena",
            defaults={"date_of_death": date.today(), "place_of_death": "Johannesburg"},
        )
        case, _ = Case.objects.get_or_create(
            tenant=tenant,
            reference="CASE-001",
            defaults={
                "branch": branch,
                "deceased": deceased,
                "status": Case.Status.IN_PROGRESS,
                "service_date": date.today() + timedelta(days=5),
                "created_by": admin,
            },
        )
        family, _ = FamilyMember.objects.get_or_create(
            tenant=tenant,
            case=case,
            first_name="Lerato",
            last_name="Mokoena",
            defaults={"relationship": "Daughter", "phone": "+27110000000", "email": "family@example.com", "is_next_of_kin": True},
        )
        ConsentRecord.objects.get_or_create(
            tenant=tenant,
            subject_name=f"{family.first_name} {family.last_name}",
            purpose="Case communications",
            defaults={"subject_email": family.email, "source": "demo seed", "recorded_by": admin},
        )

        underwriter, _ = Underwriter.objects.get_or_create(tenant=tenant, name="Ubuntu Underwriters")
        template, _ = PolicyTemplate.objects.get_or_create(
            tenant=tenant,
            underwriter=underwriter,
            name="Family Cover",
            defaults={"cover_amount": Decimal("25000.00"), "premium_amount": Decimal("150.00")},
        )
        enrollment, _ = PolicyEnrollment.objects.get_or_create(
            tenant=tenant,
            policy_number="POL-001",
            defaults={
                "policy_template": template,
                "underwriter": underwriter,
                "family_member": family,
                "start_date": date.today(),
                "created_by": admin,
            },
        )
        PremiumPayment.objects.get_or_create(
            tenant=tenant,
            enrollment=enrollment,
            due_date=date.today() + timedelta(days=30),
            defaults={"amount": Decimal("150.00"), "status": PremiumPayment.Status.PENDING},
        )

        invoice, _ = Invoice.objects.get_or_create(
            tenant=tenant,
            invoice_number="INV-001",
            defaults={
                "branch": branch,
                "case": case,
                "customer_name": "Lerato Mokoena",
                "customer_email": family.email,
                "issue_date": date.today(),
                "due_date": date.today() + timedelta(days=7),
                "status": Invoice.Status.ISSUED,
                "created_by": admin,
            },
        )
        InvoiceLineItem.objects.get_or_create(
            tenant=tenant,
            invoice=invoice,
            description="Funeral service package",
            defaults={"quantity": Decimal("1.00"), "unit_price": Decimal("8500.00")},
        )
        Payment.objects.get_or_create(
            tenant=tenant,
            invoice=invoice,
            provider_reference="DEMO-CASH-001",
            defaults={
                "amount": Decimal("2500.00"),
                "method": Payment.Method.CASH,
                "status": Payment.Status.COMPLETED,
                "received_by": admin,
                "received_at": timezone.now(),
            },
        )

        coffin, _ = InventoryItem.objects.get_or_create(
            tenant=tenant,
            branch=branch,
            sku="COFFIN-STD",
            defaults={"name": "Standard coffin", "category": "Coffins", "quantity_on_hand": Decimal("5.00"), "reorder_level": Decimal("2.00")},
        )
        InventoryTransaction.objects.get_or_create(
            tenant=tenant,
            item=coffin,
            note="Demo stock issue",
            defaults={"case": case, "transaction_type": InventoryTransaction.TransactionType.STOCK_OUT, "quantity": Decimal("1.00"), "created_by": admin},
        )

        hearse, _ = Resource.objects.get_or_create(
            tenant=tenant,
            branch=branch,
            name="Hearse 1",
            defaults={"resource_type": Resource.ResourceType.VEHICLE},
        )
        event, _ = CalendarEvent.objects.get_or_create(
            tenant=tenant,
            branch=branch,
            title="Mokoena funeral service",
            defaults={
                "case": case,
                "event_type": CalendarEvent.EventType.FUNERAL_SERVICE,
                "starts_at": timezone.now() + timedelta(days=5),
                "ends_at": timezone.now() + timedelta(days=5, hours=2),
                "location": "Johannesburg Chapel",
                "created_by": admin,
            },
        )
        event.resources.add(hearse)

        mortuary_record, _ = MortuaryRecord.objects.get_or_create(
            tenant=tenant,
            intake_reference="MOR-001",
            defaults={
                "branch": branch,
                "case": case,
                "deceased": deceased,
                "status": MortuaryRecord.Status.IN_STORAGE,
                "storage_location": "Cold Room A",
                "storage_unit": "A-01",
                "intake_at": timezone.now(),
                "created_by": admin,
            },
        )
        PreparationTask.objects.get_or_create(
            tenant=tenant,
            mortuary_record=mortuary_record,
            task_type=PreparationTask.TaskType.DRESSING,
            defaults={"status": PreparationTask.Status.TODO, "assigned_to": admin},
        )

        site, _ = WebsiteSite.objects.get_or_create(
            tenant=tenant,
            defaults={"name": "RestWell Demo", "subdomain": tenant.slug, "is_published": True},
        )
        page, _ = WebsitePage.objects.get_or_create(
            tenant=tenant,
            site=site,
            slug="home",
            defaults={"title": "RestWell Demo Funeral Services", "page_type": WebsitePage.PageType.HOME, "is_published": True},
        )
        WebsiteBlock.objects.get_or_create(
            tenant=tenant,
            page=page,
            block_type=WebsiteBlock.BlockType.HERO,
            defaults={"content": {"headline": "Dignified care for every family", "body": "Serving Johannesburg families with compassion."}, "sort_order": 1},
        )

        for title in ["Confirm tenant profile", "Upload brand assets", "Create staff users", "Run first case workflow"]:
            OnboardingTask.objects.get_or_create(tenant=tenant, title=title, defaults={"description": "Demo onboarding task."})
        HelpArticle.objects.get_or_create(
            tenant=tenant,
            slug="getting-started",
            defaults={"title": "Getting Started", "body": "Start with cases, policies, payments, and onboarding tasks."},
        )

        template, _ = NotificationTemplate.objects.get_or_create(
            tenant=tenant,
            code="case-update",
            channel=NotificationTemplate.Channel.IN_APP,
            defaults={"subject": "Case update", "body": "Your funeral service case has been updated."},
        )
        message, created = NotificationMessage.objects.get_or_create(
            tenant=tenant,
            template=template,
            recipient_user=admin,
            subject="Welcome to RestWell",
            defaults={"channel": NotificationMessage.Channel.IN_APP, "body": "Your demo workspace is ready.", "created_by": admin},
        )
        if created:
            send_notification(message)

        self.stdout.write(self.style.SUCCESS("Seeded RestWell demo tenant. Login: admin@restwell.local / RestWell123!"))
