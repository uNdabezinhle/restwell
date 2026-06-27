from django.contrib import admin

from .models import Case, CaseDocument, Deceased, FamilyMember


@admin.register(Deceased)
class DeceasedAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "tenant", "branch", "date_of_death")
    list_filter = ("tenant", "branch")
    search_fields = ("first_name", "last_name", "id_number")


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ("reference", "tenant", "branch", "deceased", "status", "service_date")
    list_filter = ("tenant", "branch", "status")
    search_fields = ("reference", "deceased__first_name", "deceased__last_name")


@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "relationship", "case", "is_next_of_kin")
    list_filter = ("tenant", "relationship", "is_next_of_kin")
    search_fields = ("first_name", "last_name", "phone", "email")


@admin.register(CaseDocument)
class CaseDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "document_type", "case", "uploaded_by", "uploaded_at")
    list_filter = ("tenant", "document_type")
    search_fields = ("title", "case__reference")
