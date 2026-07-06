from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from accounts.models import User
from tenants.models import Branch, Tenant


class UserModelTests(APITestCase):
    def test_user_can_be_scoped_to_tenant_and_branch(self):
        tenant = Tenant.objects.create(name="Dignity Care", slug="dignity-care")
        branch = Branch.objects.create(tenant=tenant, name="Johannesburg", code="JHB")

        user = User.objects.create_user(
            username="director",
            password="test-password",
            tenant=tenant,
            branch=branch,
            role=User.Role.TENANT_ADMIN,
        )

        self.assertEqual(user.tenant, tenant)
        self.assertEqual(user.branch, branch)


class JwtAuthTests(APITestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="Dignity Care", slug="dignity-care")
        self.branch = Branch.objects.create(tenant=self.tenant, name="Johannesburg", code="JHB")
        self.user = User.objects.create_user(
            username="director",
            password="test-password",
            tenant=self.tenant,
            branch=self.branch,
            role=User.Role.TENANT_ADMIN,
        )

    def test_token_generation_for_valid_user(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "director", "password": "test-password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_token_refresh(self):
        token_response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "director", "password": "test-password"},
            format="json",
        )

        response = self.client.post(
            reverse("token_refresh"),
            {"refresh": token_response.data["refresh"]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_me_requires_authentication(self):
        response = self.client.get(reverse("me"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_user_context(self):
        token_response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "director", "password": "test-password"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}")

        response = self.client.get(reverse("me"), HTTP_X_TENANT_ID=str(self.tenant.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["role"], User.Role.TENANT_ADMIN)
        self.assertEqual(response.data["tenant"], self.tenant.id)
        self.assertEqual(response.data["branch"], self.branch.id)
        self.assertEqual(response.data["request_tenant"], self.tenant.id)


class UserAdminApiTests(APITestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="Dignity Care", slug="dignity-care")
        self.branch = Branch.objects.create(tenant=self.tenant, name="Johannesburg", code="JHB")
        self.admin_user = User.objects.create_user(
            username="admin",
            password="test-password",
            tenant=self.tenant,
            branch=self.branch,
            role=User.Role.TENANT_ADMIN,
        )
        self.staff_user = User.objects.create_user(
            username="staff",
            password="test-password",
            tenant=self.tenant,
            branch=self.branch,
            role=User.Role.STAFF,
        )
        other_tenant = Tenant.objects.create(name="Other Care", slug="other-care")
        self.other_branch = Branch.objects.create(tenant=other_tenant, name="Durban", code="DBN")
        User.objects.create_user(
            username="external",
            password="test-password",
            tenant=other_tenant,
            branch=self.other_branch,
            role=User.Role.STAFF,
        )

    def authenticate(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "admin", "password": "test-password"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_tenant_admin_lists_only_own_users(self):
        self.authenticate()

        response = self.client.get(reverse("user-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = {row["username"] for row in response.data}
        self.assertIn("admin", usernames)
        self.assertNotIn("external", usernames)

    def test_tenant_admin_creates_staff_user_in_own_tenant(self):
        self.authenticate()

        response = self.client.post(
            reverse("user-list"),
            {
                "username": "arranger",
                "email": "arranger@example.com",
                "first_name": "Funeral",
                "last_name": "Arranger",
                "role": User.Role.STAFF,
                "branch": self.branch.id,
                "password": "RestWell123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="arranger")
        self.assertEqual(user.tenant, self.tenant)
        self.assertEqual(user.branch, self.branch)
        self.assertTrue(user.check_password("RestWell123!"))

    def test_tenant_admin_cannot_create_user_for_other_branch(self):
        self.authenticate()

        response = self.client.post(
            reverse("user-list"),
            {
                "username": "bad-branch",
                "role": User.Role.STAFF,
                "branch": self.other_branch.id,
                "password": "RestWell123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_staff_user_cannot_manage_users(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "staff", "password": "test-password"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

        response = self.client.get(reverse("user-list"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
