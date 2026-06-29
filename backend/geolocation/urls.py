from rest_framework.routers import DefaultRouter

from .views import LocationLogViewSet, LocationRouteViewSet

router = DefaultRouter()
router.register("routes", LocationRouteViewSet, basename="location-route")
router.register("logs", LocationLogViewSet, basename="location-log")

urlpatterns = router.urls
