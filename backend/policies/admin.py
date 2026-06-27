from django.contrib import admin

from .models import PolicyEnrollment, PolicyTemplate, PremiumPayment, Underwriter


@admin.register(Underwriter)
class UnderwriterAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "registration_number", "is_active")
    list_filter = ("tenant", "is_active")
    search_fields = ("name", "registration_number")


@admin.register(PolicyTemplate)
class PolicyTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "underwriter", "cover_amount", "premium_amount", "billing_frequency", "is_active")
    list_filter = ("tenant", "underwriter", "billing_frequency", "is_active")
    search_fields = ("name",)


@admin.register(PolicyEnrollment)
class PolicyEnrollmentAdmin(admin.ModelAdmin):
    list_display = ("policy_number", "tenant", "policy_template", "underwriter", "family_member", "status", "start_date")
    list_filter = ("tenant", "underwriter", "status")
    search_fields = ("policy_number", "family_member__first_name", "family_member__last_name")


@admin.register(PremiumPayment)
class PremiumPaymentAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "tenant", "amount", "due_date", "status", "paid_at")
    list_filter = ("tenant", "status", "due_date")
    search_fields = ("enrollment__policy_number", "reference")
