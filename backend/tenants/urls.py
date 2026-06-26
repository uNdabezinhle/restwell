from rest_framework.routers import DefaultRouter

from .views import BranchViewSet, TenantViewSet

router = DefaultRouter()
router.register("branches", BranchViewSet)
router.register("", TenantViewSet)

urlpatterns = router.urls
