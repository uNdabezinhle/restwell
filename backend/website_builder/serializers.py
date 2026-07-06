from rest_framework import serializers

from .models import WebsiteBlock, WebsitePage, WebsiteSite


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
    blocks = serializers.SerializerMethodField()

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
            "blocks",
        ]
        read_only_fields = ["id", "tenant", "created_at", "updated_at", "blocks"]

    def get_blocks(self, obj):
        return WebsiteBlockSerializer(obj.blocks.all(), many=True).data


class WebsiteBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebsiteBlock
        fields = ["id", "tenant", "page", "block_type", "content", "sort_order", "is_visible", "created_at", "updated_at"]
        read_only_fields = ["id", "tenant", "created_at", "updated_at"]
