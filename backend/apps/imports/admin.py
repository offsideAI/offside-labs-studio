from django.contrib import admin

from .models import ImportRun


@admin.register(ImportRun)
class ImportRunAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "workspace",
        "entity_type",
        "status",
        "total_rows",
        "processed_rows",
        "error_rows",
        "created_by",
        "created_at",
        "finished_at",
    )
    list_filter = ("entity_type", "status")
    search_fields = ("file_name", "workspace__slug", "created_by__email")
    readonly_fields = ("raw_content", "errors", "created_at", "started_at", "finished_at")
    autocomplete_fields = ("workspace", "created_by")
