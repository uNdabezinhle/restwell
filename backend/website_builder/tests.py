from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from branding.models import TenantBranding
from tenants.models import Branch, Tenant
from website_builder.models import WebsiteBlock, WebsitePage, WebsiteSite


class WebsiteBuilderApiTests(APITestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="RestWell Demo", slug="restwell-demo")
        self.branch = Branch.objects.create(tenant=self.tenant, name="Johannesburg", code="JHB")
        self.other_tenant = Tenant.objects.create(name="Other Care", slug="other-care")
        self.other_branch = Branch.objects.create(tenant=self.other_tenant, name="Cape Town", code="CPT")
        self.user = User.objects.create_user(
            username="website-admin",
            password="test-password",
            tenant=self.tenant,
            branch=self.branch,
            role=User.Role.TENANT_ADMIN,
        )
        User.objects.create_user(
            username="other-website-admin",
            password="test-password",
            tenant=self.other_tenant,
            branch=self.other_branch,
            role=User.Role.TENANT_ADMIN,
        )

    def authenticate(self, username="website-admin"):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": username, "password": "test-password"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def create_site(self, tenant=None, name="RestWell Demo", published=True):
        return WebsiteSite.objects.create(
            tenant=tenant or self.tenant,
            name=name,
            subdomain=(tenant or self.tenant).slug,
            is_published=published,
        )

    def test_creates_site_for_current_tenant(self):
        self.authenticate()

        response = self.client.post(
            reverse("website-site-list"),
            {"name": "RestWell Demo", "subdomain": "restwell-demo", "is_published": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["tenant"], self.tenant.id)

    def test_creates_page_for_current_tenant_site(self):
        self.authenticate()
        site = self.create_site()

        response = self.client.post(
            reverse("website-page-list"),
            {
                "site": site.id,
                "slug": "home",
                "title": "Welcome",
                "page_type": WebsitePage.PageType.HOME,
                "content": {"headline": "RestWell Demo"},
                "is_published": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["tenant"], self.tenant.id)
        self.assertEqual(response.data["content"]["headline"], "RestWell Demo")

    def test_rejects_cross_tenant_site_on_page(self):
        self.authenticate()
        other_site = self.create_site(tenant=self.other_tenant, name="Other Care")

        response = self.client.post(
            reverse("website-page-list"),
            {
                "site": other_site.id,
                "slug": "blocked",
                "title": "Blocked",
                "content": {},
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_tenant_user_only_sees_own_pages(self):
        site = self.create_site()
        own_page = WebsitePage.objects.create(tenant=self.tenant, site=site, slug="home", title="Home")
        other_site = self.create_site(tenant=self.other_tenant, name="Other Care")
        WebsitePage.objects.create(tenant=self.other_tenant, site=other_site, slug="home", title="Other Home")
        self.authenticate()

        response = self.client.get(reverse("website-page-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        page_ids = {page["id"] for page in response.data}
        self.assertEqual(page_ids, {own_page.id})

    def test_public_preview_returns_published_page_with_branding(self):
        site = self.create_site(published=True)
        TenantBranding.objects.create(tenant=self.tenant, primary_color="#123ABC", secondary_color="#456DEF")
        page = WebsitePage.objects.create(
            tenant=self.tenant,
            site=site,
            slug="home",
            title="Welcome",
            page_type=WebsitePage.PageType.HOME,
            content={"headline": "RestWell Demo"},
            is_published=True,
        )
        WebsiteBlock.objects.create(
            tenant=self.tenant,
            page=page,
            block_type=WebsiteBlock.BlockType.HERO,
            content={"headline": "Dignified care"},
            sort_order=1,
        )

        response = self.client.get(reverse("website-public-page", args=[self.tenant.slug, "home"]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Welcome")
        self.assertEqual(response.data["content"]["headline"], "RestWell Demo")
        self.assertEqual(response.data["blocks"][0]["content"]["headline"], "Dignified care")
        self.assertEqual(response.data["branding"]["primary_color"], "#123ABC")

    def test_creates_website_block_for_current_tenant_page(self):
        self.authenticate()
        site = self.create_site()
        page = WebsitePage.objects.create(tenant=self.tenant, site=site, slug="home", title="Home")

        response = self.client.post(
            reverse("website-block-list"),
            {
                "page": page.id,
                "block_type": WebsiteBlock.BlockType.TEXT,
                "content": {"body": "About our services"},
                "sort_order": 2,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["tenant"], self.tenant.id)
