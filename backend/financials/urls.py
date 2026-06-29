from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import DebtorAccountViewSet, InvoiceLineItemViewSet, InvoiceViewSet, PaymentViewSet, financial_summary

router = DefaultRouter()
router.register("invoices", InvoiceViewSet)
router.register("line-items", InvoiceLineItemViewSet)
router.register("payments", PaymentViewSet)
router.register("debtors", DebtorAccountViewSet)

urlpatterns = [
    path("summary/", financial_summary, name="financial-summary"),
] + router.urls
