from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class HealthEndpointTests(APITestCase):
    def test_live_health_returns_ok(self):
        response = self.client.get(reverse("health-live"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "ok")

    @override_settings(REDIS_URL="")
    def test_ready_health_returns_database_check(self):
        response = self.client.get(reverse("health-ready"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["checks"]["database"], "ok")
