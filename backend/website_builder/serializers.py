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
    public_json_url = serializers.SerializerMethodField()
    public_html_url = serializers.SerializerMethodField()

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
            "public_json_url",
            "public_html_url",
        ]
        read_only_fields = ["id", "tenant", "created_at", "updated_at", "blocks", "public_json_url", "public_html_url"]

    def get_blocks(self, obj):
        return WebsiteBlockSerializer(obj.blocks.all(), many=True).data

    def get_public_json_url(self, obj):
        return self._public_url(obj, "public") if obj.is_published else ""

    def get_public_html_url(self, obj):
        return self._public_url(obj, "render") if obj.is_published else ""

    def _public_url(self, obj, route):
        path = f"/api/websites/{route}/{obj.tenant.slug}/{obj.slug}/"
        request = self.context.get("request")
        return request.build_absolute_uri(path) if request else path


class WebsiteBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebsiteBlock
        fields = ["id", "tenant", "page", "block_type", "content", "sort_order", "is_visible", "created_at", "updated_at"]
        read_only_fields = ["id", "tenant", "created_at", "updated_at"]
