from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from cases.models import Case, Deceased
from geolocation.models import LocationLog, LocationRoute
from tenants.models import Branch, Tenant


class GeolocationApiTests(APITestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="RestWell Demo", slug="restwell-demo")
        self.branch = Branch.objects.create(tenant=self.tenant, name="Johannesburg", code="JHB")
        self.other_tenant = Tenant.objects.create(name="Other Care", slug="other-care")
        self.other_branch = Branch.objects.create(tenant=self.other_tenant, name="Cape Town", code="CPT")
        self.user = User.objects.create_user(
            username="geo-admin",
            password="test-password",
            tenant=self.tenant,
            branch=self.branch,
            role=User.Role.TENANT_ADMIN,
        )
        self.driver = User.objects.create_user(
            username="driver",
            password="test-password",
            tenant=self.tenant,
            branch=self.branch,
            role=User.Role.STAFF,
        )
        self.other_driver = User.objects.create_user(
            username="other-driver",
            password="test-password",
            tenant=self.other_tenant,
            branch=self.other_branch,
            role=User.Role.STAFF,
        )
        self.deceased = Deceased.objects.create(tenant=self.tenant, branch=self.branch, first_name="Thabo", last_name="Mokoena")
        self.case = Case.objects.create(tenant=self.tenant, branch=self.branch, deceased=self.deceased, reference="CASE-001")

    def authenticate(self, username="geo-admin"):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": username, "password": "test-password"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def create_route(self, status_value=LocationRoute.Status.ACTIVE):
        return LocationRoute.objects.create(
            tenant=self.tenant,
            branch=self.branch,
            case=self.case,
            name="Removal Team 1",
            assigned_to=self.driver,
            status=status_value,
            origin="Hospital",
            destination="RestWell",
        )

    def test_creates_route_for_current_tenant(self):
        self.authenticate()

        response = self.client.post(
            reverse("location-route-list"),
            {
                "branch": self.branch.id,
                "case": self.case.id,
                "name": "Removal Team 1",
                "assigned_to": self.driver.id,
                "status": LocationRoute.Status.ACTIVE,
                "origin": "Hospital",
                "destination": "RestWell",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["tenant"], self.tenant.id)

    def test_rejects_cross_tenant_assigned_user_on_route(self):
        self.authenticate()

        response = self.client.post(
            reverse("location-route-list"),
            {
                "branch": self.branch.id,
                "name": "Blocked Route",
                "assigned_to": self.other_driver.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_records_location_log_for_route(self):
        self.authenticate()
        route = self.create_route()

        response = self.client.post(
            reverse("location-log-list"),
            {
                "route": route.id,
                "user": self.driver.id,
                "case": self.case.id,
                "latitude": "-26.204100",
                "longitude": "28.047300",
                "accuracy_meters": "12.50",
                "recorded_at": timezone.now().isoformat(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["tenant"], self.tenant.id)

    def test_active_routes_include_latest_log(self):
        self.authenticate()
        route = self.create_route()
        LocationLog.objects.create(
            tenant=self.tenant,
            route=route,
            user=self.driver,
            case=self.case,
            latitude="-26.204100",
            longitude="28.047300",
            recorded_at=timezone.now(),
        )

        response = self.client.get(reverse("location-route-active"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], route.id)
        self.assertIsNotNone(response.data[0]["latest_log"])

    def test_tenant_user_only_sees_own_routes(self):
        own_route = self.create_route()
        LocationRoute.objects.create(
            tenant=self.other_tenant,
            branch=self.other_branch,
            name="Other Route",
            assigned_to=self.other_driver,
            status=LocationRoute.Status.ACTIVE,
        )
        self.authenticate()

        response = self.client.get(reverse("location-route-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        route_ids = {route["id"] for route in response.data}
        self.assertEqual(route_ids, {own_route.id})
