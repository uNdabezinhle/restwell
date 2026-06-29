from rest_framework.routers import DefaultRouter

from .views import AppBuildRequestViewSet, TenantAppConfigViewSet

router = DefaultRouter()
router.register("configs", TenantAppConfigViewSet, basename="tenant-app-config")
router.register("build-requests", AppBuildRequestViewSet, basename="app-build-request")

urlpatterns = router.urls
