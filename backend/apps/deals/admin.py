from django.contrib import admin

from .models import Deal, Pipeline


@admin.register(Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    list_display = ("name", "workspace", "is_default", "created_at")
    list_filter = ("is_default",)
    search_fields = ("name", "workspace__slug")
    autocomplete_fields = ("workspace", "created_by")


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "workspace",
        "pipeline",
        "stage_id",
        "value_cents",
        "currency",
        "owner",
        "created_at",
        "deleted_at",
    )
    list_filter = ("currency",)
    search_fields = ("name", "workspace__slug", "company__name", "contact__primary_email")
    autocomplete_fields = ("workspace", "pipeline", "contact", "company", "owner", "created_by")
    readonly_fields = ("created_at", "updated_at")
