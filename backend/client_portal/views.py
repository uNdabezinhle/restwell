from django.utils import timezone
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from branding.models import TenantBranding
from cases.models import CaseDocument, FamilyMember
from financials.models import Invoice
from notifications.models import NotificationMessage
from policies.models import PolicyEnrollment
from scheduling.models import CalendarEvent
from website_builder.models import WebsitePage
from .models import ClientSupportRequest
from .serializers import ClientSupportRequestSerializer


def family_members_for_user(user):
    if not user.tenant_id or not user.email:
        return FamilyMember.objects.none()
    return FamilyMember.objects.filter(tenant=user.tenant, email__iexact=user.email).select_related("case", "tenant")


def require_family_context(user):
    family_members = family_members_for_user(user)
    if not family_members.exists() and not user.is_tenant_admin and not user.is_platform_admin:
        raise PermissionDenied("No family profile is linked to this account.")
    return family_members


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def client_dashboard(request):
    family_members = require_family_context(request.user)
    tenant = request.user.tenant
    case_ids = list(family_members.values_list("case_id", flat=True))
    branding = TenantBranding.objects.filter(tenant=tenant, is_active=True).first() if tenant else None
    policies = PolicyEnrollment.objects.filter(tenant=tenant, family_member__in=family_members).select_related("policy_template", "underwriter")
    invoices = Invoice.objects.filter(tenant=tenant, case_id__in=case_ids).prefetch_related("payments").order_by("-issue_date", "-id")
    events = CalendarEvent.objects.filter(tenant=tenant, case_id__in=case_ids).order_by("starts_at")
    documents = CaseDocument.objects.filter(tenant=tenant, case_id__in=case_ids).order_by("-uploaded_at")
    notifications = NotificationMessage.objects.filter(tenant=tenant, recipient_user=request.user).order_by("-created_at")[:10]
    support_requests = ClientSupportRequest.objects.filter(tenant=tenant, created_by=request.user).order_by("-created_at")[:10]
    public_pages = WebsitePage.objects.filter(
        tenant=tenant,
        site__is_published=True,
        is_published=True,
    ).select_related("site").order_by("sort_order", "title")

    return Response(
        {
            "tenant": {"id": tenant.id, "name": tenant.name, "slug": tenant.slug} if tenant else None,
            "branding": {
                "primary_color": branding.primary_color if branding else "#0F766E",
                "secondary_color": branding.secondary_color if branding else "#2563EB",
                "logo": branding.logo.url if branding and branding.logo else "",
            },
            "family_members": [
                {
                    "id": member.id,
                    "name": f"{member.first_name} {member.last_name}".strip(),
                    "relationship": member.relationship,
                    "case": member.case_id,
                    "is_next_of_kin": member.is_next_of_kin,
                }
                for member in family_members
            ],
            "cases": [
                {
                    "id": member.case.id,
                    "reference": member.case.reference,
                    "status": member.case.status,
                    "service_date": member.case.service_date,
                    "notes": member.case.notes,
                    "branch": member.case.branch.name,
                    "deceased": str(member.case.deceased),
                    "deceased_details": {
                        "first_name": member.case.deceased.first_name,
                        "last_name": member.case.deceased.last_name,
                        "date_of_death": member.case.deceased.date_of_death,
                        "place_of_death": member.case.deceased.place_of_death,
                    },
                }
                for member in family_members.select_related("case", "case__branch", "case__deceased")
            ],
            "policies": [
                {
                    "id": policy.id,
                    "policy_number": policy.policy_number,
                    "status": policy.status,
                    "template": policy.policy_template.name,
                    "underwriter": policy.underwriter.name,
                }
                for policy in policies
            ],
            "financials": {
                "invoice_count": invoices.count(),
                "total_amount": sum(invoice.total_amount for invoice in invoices),
                "amount_paid": sum(invoice.amount_paid for invoice in invoices),
                "balance_due": sum(invoice.balance_due for invoice in invoices),
            },
            "invoices": [
                {
                    "id": invoice.id,
                    "invoice_number": invoice.invoice_number,
                    "case": invoice.case_id,
                    "customer_name": invoice.customer_name,
                    "issue_date": invoice.issue_date,
                    "due_date": invoice.due_date,
                    "status": invoice.status,
                    "total_amount": invoice.total_amount,
                    "amount_paid": invoice.amount_paid,
                    "balance_due": invoice.balance_due,
                    "payments": [
                        {
                            "id": payment.id,
                            "amount": payment.amount,
                            "method": payment.method,
                            "status": payment.status,
                            "received_at": payment.received_at,
                        }
                        for payment in invoice.payments.all()
                    ],
                }
                for invoice in invoices
            ],
            "events": [
                {
                    "id": event.id,
                    "case": event.case_id,
                    "title": event.title,
                    "event_type": event.event_type,
                    "starts_at": event.starts_at,
                    "ends_at": event.ends_at,
                    "location": event.location,
                }
                for event in events
            ],
            "documents": [
                {
                    "id": document.id,
                    "case": document.case_id,
                    "title": document.title,
                    "document_type": document.document_type,
                    "file": document.file.url if document.file else "",
                    "uploaded_at": document.uploaded_at,
                }
                for document in documents
            ],
            "notifications": [
                {
                    "id": message.id,
                    "subject": message.subject,
                    "body": message.body,
                    "status": message.status,
                    "created_at": message.created_at,
                }
                for message in notifications
            ],
            "support_requests": [
                {
                    "id": support.id,
                    "subject": support.subject,
                    "message": support.message,
                    "status": support.status,
                    "created_at": support.created_at,
                }
                for support in support_requests
            ],
            "public_pages": [
                {
                    "id": page.id,
                    "title": page.title,
                    "slug": page.slug,
                    "page_type": page.page_type,
                    "url": f"/api/websites/public/{tenant.slug}/{page.slug}/",
                }
                for page in public_pages
            ],
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, pk):
    family_members = require_family_context(request.user)
    message = NotificationMessage.objects.filter(
        id=pk,
        tenant=request.user.tenant,
        recipient_user=request.user,
    ).first()
    if not message:
        raise PermissionDenied("Notification is not available for this account.")
    message.status = NotificationMessage.Status.READ
    message.read_at = timezone.now()
    message.save(update_fields=["status", "read_at"])
    return Response(
        {
            "id": message.id,
            "subject": message.subject,
            "status": message.status,
            "read_at": message.read_at,
            "family_profiles": family_members.count(),
        }
    )


class ClientSupportRequestViewSet(ModelViewSet):
    serializer_class = ClientSupportRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_platform_admin:
            return ClientSupportRequest.objects.all()
        if not user.tenant_id:
            return ClientSupportRequest.objects.none()
        queryset = ClientSupportRequest.objects.filter(tenant=user.tenant)
        if user.is_tenant_admin:
            return queryset
        return queryset.filter(created_by=user)

    def perform_create(self, serializer):
        family_members = require_family_context(self.request.user)
        family_member = family_members.first()
        if not self.request.user.tenant_id:
            raise ValidationError("A tenant-scoped user is required.")
        serializer.save(tenant=self.request.user.tenant, family_member=family_member, created_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="resolve")
    def resolve(self, request, pk=None):
        support_request = self.get_object()
        if not request.user.is_tenant_admin and not request.user.is_platform_admin:
            raise PermissionDenied("Only tenant administrators can resolve support requests.")
        support_request.status = ClientSupportRequest.Status.RESOLVED
        support_request.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(support_request).data)
