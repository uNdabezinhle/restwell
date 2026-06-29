from django.contrib import admin

from .models import MortuaryRecord, PreparationTask


class PreparationTaskInline(admin.TabularInline):
    model = PreparationTask
    extra = 0


@admin.register(MortuaryRecord)
class MortuaryRecordAdmin(admin.ModelAdmin):
    list_display = ["intake_reference", "tenant", "branch", "deceased", "status", "storage_location", "storage_unit"]
    list_filter = ["status", "branch"]
    search_fields = ["intake_reference", "deceased__first_name", "deceased__last_name", "storage_unit"]
    inlines = [PreparationTaskInline]


@admin.register(PreparationTask)
class PreparationTaskAdmin(admin.ModelAdmin):
    list_display = ["mortuary_record", "task_type", "status", "assigned_to", "due_at", "completed_at"]
    list_filter = ["task_type", "status"]
    search_fields = ["mortuary_record__intake_reference", "notes"]
