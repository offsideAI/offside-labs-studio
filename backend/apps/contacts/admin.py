from django.contrib import admin

from .models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = (
        "primary_email",
        "first_name",
        "last_name",
        "company",
        "workspace",
        "lifecycle_stage",
        "created_at",
        "deleted_at",
    )
    list_filter = ("lifecycle_stage",)
    search_fields = ("primary_email", "first_name", "last_name", "company__name", "workspace__slug")
    autocomplete_fields = ("workspace", "company", "owner", "created_by")
    readonly_fields = ("created_at", "updated_at")
