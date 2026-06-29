from rest_framework.routers import DefaultRouter

from .views import CalendarEventViewSet, ResourceViewSet

router = DefaultRouter()
router.register("resources", ResourceViewSet)
router.register("events", CalendarEventViewSet)

urlpatterns = router.urls
