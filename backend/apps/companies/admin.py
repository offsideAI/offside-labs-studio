from django.contrib import admin

from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "workspace", "domain", "size_band", "industry", "created_at", "deleted_at")
    list_filter = ("size_band",)
    search_fields = ("name", "domain", "industry", "workspace__slug")
    autocomplete_fields = ("workspace", "owner", "created_by")
    readonly_fields = ("created_at", "updated_at")
