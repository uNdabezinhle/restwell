from rest_framework.routers import DefaultRouter

from .views import InventoryItemViewSet, InventoryTransactionViewSet

router = DefaultRouter()
router.register("items", InventoryItemViewSet)
router.register("transactions", InventoryTransactionViewSet)

urlpatterns = router.urls
