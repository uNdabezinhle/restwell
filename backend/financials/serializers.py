from rest_framework import serializers

from .models import DebtorAccount, Invoice, InvoiceLineItem, Payment


class InvoiceLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceLineItem
        fields = ["id", "tenant", "invoice", "description", "quantity", "unit_price", "tax_amount", "line_total"]
        read_only_fields = ["id", "tenant", "line_total"]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "tenant",
            "invoice",
            "amount",
            "method",
            "status",
            "provider_reference",
            "received_by",
            "received_at",
            "created_at",
        ]
        read_only_fields = ["id", "tenant", "received_by", "created_at"]


class InvoiceSerializer(serializers.ModelSerializer):
    line_items = InvoiceLineItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    balance_due = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "tenant",
            "branch",
            "case",
            "policy_enrollment",
            "invoice_number",
            "customer_name",
            "customer_email",
            "issue_date",
            "due_date",
            "status",
            "subtotal",
            "tax_amount",
            "total_amount",
            "amount_paid",
            "balance_due",
            "created_by",
            "created_at",
            "line_items",
            "payments",
        ]
        read_only_fields = ["id", "tenant", "subtotal", "tax_amount", "total_amount", "amount_paid", "created_by", "created_at"]


class DebtorAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = DebtorAccount
        fields = ["id", "tenant", "invoice", "customer_name", "amount_due", "status", "updated_at"]
        read_only_fields = fields
