from django.contrib import admin

from .models import DebtorAccount, Invoice, InvoiceLineItem, Payment


class InvoiceLineItemInline(admin.TabularInline):
    model = InvoiceLineItem
    extra = 0


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "tenant", "customer_name", "status", "total_amount", "amount_paid", "due_date")
    list_filter = ("tenant", "branch", "status")
    search_fields = ("invoice_number", "customer_name", "customer_email")
    inlines = [InvoiceLineItemInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("invoice", "tenant", "amount", "method", "status", "received_at")
    list_filter = ("tenant", "method", "status")
    search_fields = ("invoice__invoice_number", "provider_reference")


@admin.register(DebtorAccount)
class DebtorAccountAdmin(admin.ModelAdmin):
    list_display = ("customer_name", "tenant", "invoice", "amount_due", "status", "updated_at")
    list_filter = ("tenant", "status")
    search_fields = ("customer_name", "invoice__invoice_number")
