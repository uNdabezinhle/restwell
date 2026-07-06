from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AuditLogViewSet,
    ConsentRecordViewSet,
    DataSubjectRequestViewSet,
    TenantFeatureViewSet,
    dashboard_summary,
)

router = DefaultRouter()
router.register("features", TenantFeatureViewSet, basename="tenant-feature")
router.register("audit-logs", AuditLogViewSet, basename="audit-log")
router.register("consents", ConsentRecordViewSet, basename="consent-record")
router.register("data-requests", DataSubjectRequestViewSet, basename="data-subject-request")

urlpatterns = [
    path("dashboard/summary/", dashboard_summary, name="dashboard-summary"),
] + router.urls
