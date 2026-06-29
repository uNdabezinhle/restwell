from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from cases.models import Case, Deceased
from scheduling.models import CalendarEvent, Resource
from tenants.models import Branch, Tenant


class SchedulingApiTests(APITestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="RestWell Demo", slug="restwell-demo")
        self.branch = Branch.objects.create(tenant=self.tenant, name="Johannesburg", code="JHB")
        self.other_tenant = Tenant.objects.create(name="Other Care", slug="other-care")
        self.other_branch = Branch.objects.create(tenant=self.other_tenant, name="Cape Town", code="CPT")
        self.user = User.objects.create_user(
            username="schedule-admin",
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
            {"username": "schedule-admin", "password": "test-password"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def create_resource(self, tenant=None, branch=None, name="Hearse 1"):
        return Resource.objects.create(
            tenant=tenant or self.tenant,
            branch=branch or self.branch,
            name=name,
            resource_type=Resource.ResourceType.VEHICLE,
        )

    def test_creates_resource_for_current_tenant(self):
        self.authenticate()

        response = self.client.post(
            reverse("resource-list"),
            {
                "branch": self.branch.id,
                "name": "Hearse 1",
                "resource_type": Resource.ResourceType.VEHICLE,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["tenant"], self.tenant.id)

    def test_creates_calendar_event_with_resource(self):
        self.authenticate()
        resource = self.create_resource()
        starts_at = timezone.now() + timedelta(days=1)
        ends_at = starts_at + timedelta(hours=2)

        response = self.client.post(
            reverse("calendarevent-list"),
            {
                "branch": self.branch.id,
                "case": self.case.id,
                "title": "Funeral Service",
                "event_type": CalendarEvent.EventType.FUNERAL_SERVICE,
                "starts_at": starts_at.isoformat(),
                "ends_at": ends_at.isoformat(),
                "resources": [resource.id],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["tenant"], self.tenant.id)
        self.assertEqual(response.data["created_by"], self.user.id)

    def test_rejects_resource_scheduling_conflict(self):
        self.authenticate()
        resource = self.create_resource()
        starts_at = timezone.now() + timedelta(days=1)
        ends_at = starts_at + timedelta(hours=2)
        event = CalendarEvent.objects.create(
            tenant=self.tenant,
            branch=self.branch,
            case=self.case,
            title="Existing Service",
            starts_at=starts_at,
            ends_at=ends_at,
        )
        event.resources.add(resource)

        response = self.client.post(
            reverse("calendarevent-list"),
            {
                "branch": self.branch.id,
                "case": self.case.id,
                "title": "Conflicting Service",
                "event_type": CalendarEvent.EventType.FUNERAL_SERVICE,
                "starts_at": (starts_at + timedelta(minutes=30)).isoformat(),
                "ends_at": (ends_at + timedelta(minutes=30)).isoformat(),
                "resources": [resource.id],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_tenant_user_only_sees_own_events(self):
        resource = self.create_resource()
        starts_at = timezone.now() + timedelta(days=1)
        own_event = CalendarEvent.objects.create(
            tenant=self.tenant,
            branch=self.branch,
            case=self.case,
            title="Own Service",
            starts_at=starts_at,
            ends_at=starts_at + timedelta(hours=2),
        )
        own_event.resources.add(resource)
        other_event = CalendarEvent.objects.create(
            tenant=self.other_tenant,
            branch=self.other_branch,
            title="Other Service",
            starts_at=starts_at,
            ends_at=starts_at + timedelta(hours=2),
        )
        self.authenticate()

        response = self.client.get(reverse("calendarevent-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        event_ids = {event["id"] for event in response.data}
        self.assertEqual(event_ids, {own_event.id})
        self.assertNotIn(other_event.id, event_ids)
