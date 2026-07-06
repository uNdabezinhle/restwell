from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from notifications.models import NotificationDeliveryLog, NotificationMessage, NotificationTemplate
from tenants.models import Branch, Tenant


class NotificationApiTests(APITestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="RestWell Demo", slug="restwell-demo")
        self.branch = Branch.objects.create(tenant=self.tenant, name="Johannesburg", code="JHB")
        self.user = User.objects.create_user(
            username="notify-admin",
            password="test-password",
            tenant=self.tenant,
            branch=self.branch,
            role=User.Role.TENANT_ADMIN,
        )

    def authenticate(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "notify-admin", "password": "test-password"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_creates_and_sends_local_notification(self):
        self.authenticate()
        template = NotificationTemplate.objects.create(
            tenant=self.tenant,
            code="case-update",
            channel=NotificationTemplate.Channel.IN_APP,
            subject="Case update",
            body="Your case has been updated.",
        )

        create_response = self.client.post(
            reverse("notification-message-list"),
            {
                "template": template.id,
                "recipient_user": self.user.id,
                "channel": NotificationMessage.Channel.IN_APP,
                "subject": "Welcome",
                "body": "Your workspace is ready.",
            },
            format="json",
        )
        send_response = self.client.post(reverse("notification-message-send", args=[create_response.data["id"]]))

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(send_response.status_code, status.HTTP_200_OK)
        self.assertEqual(send_response.data["status"], NotificationMessage.Status.SENT)
        self.assertEqual(NotificationDeliveryLog.objects.count(), 1)

    def test_inbox_returns_user_notifications(self):
        NotificationMessage.objects.create(
            tenant=self.tenant,
            recipient_user=self.user,
            channel=NotificationMessage.Channel.IN_APP,
            subject="Hello",
            body="Message",
        )
        self.authenticate()

        response = self.client.get(reverse("notification-inbox-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
