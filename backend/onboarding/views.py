from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from accounts.permissions import IsTenantAdminOrPlatformAdmin
from .models import HelpArticle, OnboardingTask, TenantOnboardingStatus
from .serializers import HelpArticleSerializer, OnboardingTaskSerializer, TenantOnboardingStatusSerializer


class TenantScopedOnboardingViewSet(ModelViewSet):
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


class TenantOnboardingStatusViewSet(TenantScopedOnboardingViewSet):
    queryset = TenantOnboardingStatus.objects.select_related("tenant")
    serializer_class = TenantOnboardingStatusSerializer

    def perform_create(self, serializer):
        tenant = self.current_tenant()
        if TenantOnboardingStatus.objects.filter(tenant=tenant).exists():
            raise ValidationError({"tenant": "Onboarding status already exists for this tenant."})
        serializer.save(tenant=tenant)

    def perform_update(self, serializer):
        serializer.save(tenant=serializer.instance.tenant)


class OnboardingTaskViewSet(TenantScopedOnboardingViewSet):
    queryset = OnboardingTask.objects.select_related("tenant", "completed_by")
    serializer_class = OnboardingTaskSerializer

    def perform_create(self, serializer):
        serializer.save(tenant=self.current_tenant())

    @action(detail=True, methods=["post"], url_path="complete")
    def complete(self, request, pk=None):
        task = self.get_object()
        task.completed_by = request.user
        task.completed_at = timezone.now()
        task.save(update_fields=["completed_by", "completed_at"])
        serializer = self.get_serializer(task)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        queryset = self.get_queryset()
        total = queryset.count()
        completed = queryset.exclude(completed_at__isnull=True).count()
        required_open = queryset.filter(is_required=True, completed_at__isnull=True).count()
        return Response({"total": total, "completed": completed, "required_open": required_open})


class HelpArticleViewSet(TenantScopedOnboardingViewSet):
    queryset = HelpArticle.objects.select_related("tenant")
    serializer_class = HelpArticleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_platform_admin:
            return queryset
        return queryset.filter(is_published=True)

    def perform_create(self, serializer):
        serializer.save(tenant=self.current_tenant())


class PublishedHelpArticleViewSet(ReadOnlyModelViewSet):
    serializer_class = HelpArticleSerializer
    permission_classes = [IsTenantAdminOrPlatformAdmin]

    def get_queryset(self):
        user = self.request.user
        queryset = HelpArticle.objects.filter(is_published=True).select_related("tenant")
        if user.is_platform_admin:
            return queryset
        return queryset.filter(tenant__isnull=True) | queryset.filter(tenant=user.tenant)
