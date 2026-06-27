from rest_framework.routers import DefaultRouter

from .views import CaseDocumentViewSet, CaseViewSet, DeceasedViewSet, FamilyMemberViewSet

router = DefaultRouter()
router.register("deceased", DeceasedViewSet)
router.register("family-members", FamilyMemberViewSet)
router.register("documents", CaseDocumentViewSet)
router.register("", CaseViewSet)

urlpatterns = router.urls
