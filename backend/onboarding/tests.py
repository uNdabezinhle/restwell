from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from onboarding.models import HelpArticle, OnboardingTask, TenantOnboardingStatus
from tenants.models import Branch, Tenant


class OnboardingApiTests(APITestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="RestWell Demo", slug="restwell-demo")
        self.branch = Branch.objects.create(tenant=self.tenant, name="Johannesburg", code="JHB")
        self.other_tenant = Tenant.objects.create(name="Other Care", slug="other-care")
        self.other_branch = Branch.objects.create(tenant=self.other_tenant, name="Cape Town", code="CPT")
        self.user = User.objects.create_user(
            username="onboarding-admin",
            password="test-password",
            tenant=self.tenant,
            branch=self.branch,
            role=User.Role.TENANT_ADMIN,
        )
        User.objects.create_user(
            username="other-onboarding-admin",
            password="test-password",
            tenant=self.other_tenant,
            branch=self.other_branch,
            role=User.Role.TENANT_ADMIN,
        )

    def authenticate(self, username="onboarding-admin"):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": username, "password": "test-password"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_creates_onboarding_status_for_current_tenant(self):
        self.authenticate()

        response = self.client.post(
            reverse("onboarding-status-list"),
            {"status": TenantOnboardingStatus.Status.IN_PROGRESS, "current_step": "branding"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["tenant"], self.tenant.id)

    def test_creates_and_completes_onboarding_task(self):
        self.authenticate()
        create_response = self.client.post(
            reverse("onboarding-task-list"),
            {
                "title": "Upload logo",
                "description": "Add tenant logo and brand colors.",
                "category": OnboardingTask.Category.BRANDING,
                "sort_order": 10,
            },
            format="json",
        )

        response = self.client.post(reverse("onboarding-task-complete", args=[create_response.data["id"]]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_completed"])
        self.assertEqual(response.data["completed_by"], self.user.id)

    def test_task_summary_counts_open_required_tasks(self):
        OnboardingTask.objects.create(tenant=self.tenant, title="Create users", category=OnboardingTask.Category.USERS)
        OnboardingTask.objects.create(
            tenant=self.tenant,
            title="Optional training",
            category=OnboardingTask.Category.TRAINING,
            is_required=False,
        )
        self.authenticate()

        response = self.client.get(reverse("onboarding-task-summary"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total"], 2)
        self.assertEqual(response.data["required_open"], 1)

    def test_tenant_user_only_sees_own_tasks(self):
        own_task = OnboardingTask.objects.create(tenant=self.tenant, title="Create users")
        OnboardingTask.objects.create(tenant=self.other_tenant, title="Other users")
        self.authenticate()

        response = self.client.get(reverse("onboarding-task-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task_ids = {task["id"] for task in response.data}
        self.assertEqual(task_ids, {own_task.id})

    def test_published_help_articles_include_global_and_tenant_articles(self):
        global_article = HelpArticle.objects.create(
            slug="getting-started",
            title="Getting Started",
            body="Start with users, branding, and your first case.",
        )
        tenant_article = HelpArticle.objects.create(
            tenant=self.tenant,
            slug="demo-training",
            title="Demo Training",
            body="Tenant-specific training checklist.",
        )
        HelpArticle.objects.create(
            tenant=self.other_tenant,
            slug="other-training",
            title="Other Training",
            body="Hidden from this tenant.",
        )
        self.authenticate()

        response = self.client.get(reverse("published-help-article-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        article_ids = {article["id"] for article in response.data}
        self.assertEqual(article_ids, {global_article.id, tenant_article.id})
