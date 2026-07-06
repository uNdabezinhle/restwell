from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ClientSupportRequestViewSet, client_dashboard

router = DefaultRouter()
router.register("support-requests", ClientSupportRequestViewSet, basename="client-support-request")

urlpatterns = [
    path("dashboard/", client_dashboard, name="client-dashboard"),
] + router.urls
