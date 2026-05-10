from django.contrib import admin

from .models import Activity


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("kind", "workspace", "related_type", "related_id", "actor_user", "occurred_at")
    list_filter = ("kind", "actor_kind", "related_type")
    search_fields = ("workspace__slug", "actor_user__email")
    readonly_fields = ("occurred_at",)
    autocomplete_fields = ("workspace", "actor_user")
