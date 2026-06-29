from rest_framework import serializers

from .models import WebsitePage, WebsiteSite


class WebsiteSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebsiteSite
        fields = [
            "id",
            "tenant",
            "name",
            "subdomain",
            "custom_domain",
            "is_published",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "tenant", "created_at", "updated_at"]


class WebsitePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebsitePage
        fields = [
            "id",
            "tenant",
            "site",
            "slug",
            "title",
            "page_type",
            "content",
            "sort_order",
            "is_published",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "tenant", "created_at", "updated_at"]
