from rest_framework.routers import DefaultRouter

from .views import PolicyEnrollmentViewSet, PolicyTemplateViewSet, PremiumPaymentViewSet, UnderwriterViewSet

router = DefaultRouter()
router.register("underwriters", UnderwriterViewSet)
router.register("templates", PolicyTemplateViewSet)
router.register("enrollments", PolicyEnrollmentViewSet)
router.register("premium-payments", PremiumPaymentViewSet)

urlpatterns = router.urls
