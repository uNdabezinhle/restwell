from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts.permissions import IsTenantAdminOrPlatformAdmin
from .models import AppBuildRequest, TenantAppConfig
from .serializers import AppBuildRequestSerializer, TenantAppConfigSerializer


class TenantScopedBrandedAppViewSet(ModelViewSet):
    permission_classes = [IsTenantAdminOrPlatformAdmin]
    tenant_field = "tenant_id"

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_platform_admin:
            return queryset
        if user.tenant_id:
            return queryset.filter(**{self.tenant_field: user.tenant_id})
        return queryset.none()

    def current_tenant(self):
        if not self.request.user.tenant_id:
            raise ValidationError("A tenant-scoped user is required.")
        return self.request.user.tenant


class TenantAppConfigViewSet(TenantScopedBrandedAppViewSet):
    queryset = TenantAppConfig.objects.select_related("tenant")
    serializer_class = TenantAppConfigSerializer

    def perform_create(self, serializer):
        tenant = self.current_tenant()
        if TenantAppConfig.objects.filter(tenant=tenant).exists():
            raise ValidationError({"tenant": "App configuration already exists for this tenant."})
        serializer.save(tenant=tenant)

    def perform_update(self, serializer):
        serializer.save(tenant=serializer.instance.tenant)

    @action(detail=True, methods=["post"], url_path="request-build")
    def request_build(self, request, pk=None):
        app_config = self.get_object()
        build_request = AppBuildRequest.objects.create(
            tenant=app_config.tenant,
            app_config=app_config,
            platform=AppBuildRequest.Platform.ANDROID,
            requested_by=request.user,
            git_ref=request.data.get("git_ref", ""),
        )
        serializer = AppBuildRequestSerializer(build_request)
        return Response(serializer.data, status=201)


class AppBuildRequestViewSet(TenantScopedBrandedAppViewSet):
    queryset = AppBuildRequest.objects.select_related("tenant", "app_config", "requested_by")
    serializer_class = AppBuildRequestSerializer

    def perform_create(self, serializer):
        tenant = self.current_tenant()
        app_config = serializer.validated_data["app_config"]
        if app_config.tenant_id != tenant.id:
            raise ValidationError({"app_config": "App config must belong to the current tenant."})
        serializer.save(tenant=tenant, requested_by=self.request.user)
