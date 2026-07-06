from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from branding.models import TenantBranding
from cases.models import FamilyMember
from notifications.models import NotificationMessage
from policies.models import PolicyEnrollment
from scheduling.models import CalendarEvent
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
    events = CalendarEvent.objects.filter(tenant=tenant, case_id__in=case_ids).order_by("starts_at")
    notifications = NotificationMessage.objects.filter(tenant=tenant, recipient_user=request.user).order_by("-created_at")[:10]

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
                    "deceased": str(member.case.deceased),
                }
                for member in family_members.select_related("case", "case__deceased")
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
            "events": [
                {
                    "id": event.id,
                    "title": event.title,
                    "starts_at": event.starts_at,
                    "ends_at": event.ends_at,
                    "location": event.location,
                }
                for event in events
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
