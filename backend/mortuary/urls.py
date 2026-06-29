from rest_framework.routers import DefaultRouter

from .views import MortuaryRecordViewSet, PreparationTaskViewSet

router = DefaultRouter()
router.register("records", MortuaryRecordViewSet, basename="mortuary-record")
router.register("preparation-tasks", PreparationTaskViewSet, basename="preparation-task")

urlpatterns = router.urls
