from django.db import models


class WebsiteSite(models.Model):
    tenant = models.OneToOneField("tenants.Tenant", related_name="website_site", on_delete=models.CASCADE)
    name = models.CharField(max_length=180)
    subdomain = models.SlugField(max_length=80, blank=True)
    custom_domain = models.CharField(max_length=180, blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["tenant__name"]

    def __str__(self):
        return self.name


class WebsitePage(models.Model):
    class PageType(models.TextChoices):
        HOME = "home", "Home"
        SERVICES = "services", "Services"
        MEMORIAL = "memorial", "Memorial"
        CONTACT = "contact", "Contact"
        CUSTOM = "custom", "Custom"

    tenant = models.ForeignKey("tenants.Tenant", related_name="website_pages", on_delete=models.CASCADE)
    site = models.ForeignKey(WebsiteSite, related_name="pages", on_delete=models.CASCADE)
    slug = models.SlugField(max_length=120)
    title = models.CharField(max_length=180)
    page_type = models.CharField(max_length=40, choices=PageType.choices, default=PageType.CUSTOM)
    content = models.JSONField(default=dict, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["site", "sort_order", "title"]
        constraints = [
            models.UniqueConstraint(fields=["site", "slug"], name="unique_website_page_slug_per_site"),
        ]

    def __str__(self):
        return f"{self.site}: {self.title}"
