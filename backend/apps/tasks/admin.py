from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "workspace",
        "related_type",
        "related_id",
        "status",
        "priority",
        "owner",
        "due_at",
        "created_at",
    )
    list_filter = ("status", "priority", "related_type")
    search_fields = ("title", "workspace__slug")
    autocomplete_fields = ("workspace", "owner", "created_by")
    readonly_fields = ("created_at", "updated_at")
