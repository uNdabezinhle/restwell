from django.contrib import admin

from .models import WebsitePage, WebsiteSite


class WebsitePageInline(admin.TabularInline):
    model = WebsitePage
    extra = 0


@admin.register(WebsiteSite)
class WebsiteSiteAdmin(admin.ModelAdmin):
    list_display = ["name", "tenant", "subdomain", "custom_domain", "is_published"]
    list_filter = ["is_published"]
    search_fields = ["name", "tenant__name", "subdomain", "custom_domain"]
    inlines = [WebsitePageInline]


@admin.register(WebsitePage)
class WebsitePageAdmin(admin.ModelAdmin):
    list_display = ["title", "site", "tenant", "page_type", "slug", "is_published"]
    list_filter = ["page_type", "is_published"]
    search_fields = ["title", "slug", "site__name", "tenant__name"]
