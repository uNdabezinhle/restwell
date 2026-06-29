from rest_framework.routers import DefaultRouter

from .views import HelpArticleViewSet, OnboardingTaskViewSet, PublishedHelpArticleViewSet, TenantOnboardingStatusViewSet

router = DefaultRouter()
router.register("statuses", TenantOnboardingStatusViewSet, basename="onboarding-status")
router.register("tasks", OnboardingTaskViewSet, basename="onboarding-task")
router.register("articles", HelpArticleViewSet, basename="help-article")
router.register("published-articles", PublishedHelpArticleViewSet, basename="published-help-article")

urlpatterns = router.urls
