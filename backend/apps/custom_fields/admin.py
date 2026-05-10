from django.contrib import admin

from .models import CustomFieldDef


@admin.register(CustomFieldDef)
class CustomFieldDefAdmin(admin.ModelAdmin):
    list_display = ("workspace", "entity_type", "key", "label", "type", "required", "order")
    list_filter = ("entity_type", "type", "required")
    search_fields = ("key", "label", "workspace__slug")
    autocomplete_fields = ("workspace",)
    ordering = ("workspace", "entity_type", "order", "key")
