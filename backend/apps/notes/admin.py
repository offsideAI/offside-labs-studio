from django.contrib import admin

from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("id", "workspace", "related_type", "related_id", "author", "created_at", "deleted_at")
    list_filter = ("related_type",)
    search_fields = ("body_md", "workspace__slug", "author__email")
    autocomplete_fields = ("workspace", "author")
    readonly_fields = ("edit_log", "created_at", "updated_at")
