from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import WebsitePageViewSet, WebsiteSiteViewSet, public_page

router = DefaultRouter()
router.register("sites", WebsiteSiteViewSet, basename="website-site")
router.register("pages", WebsitePageViewSet, basename="website-page")

urlpatterns = [
    path("public/<slug:tenant_slug>/<slug:page_slug>/", public_page, name="website-public-page"),
] + router.urls
