from django.test import TestCase

from accounts.models import User
from tenants.models import Branch, Tenant


class UserModelTests(TestCase):
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
