"""Django admin for the Agents Marketplace."""

from __future__ import annotations

from django.contrib import admin

from .models import MarketplaceAgent, WorkspaceAgentInstall


@admin.register(MarketplaceAgent)
class MarketplaceAgentAdmin(admin.ModelAdmin):
    list_display = (
        "icon_emoji",
        "name",
        "slug",
        "category",
        "install_count",
        "is_published",
        "author",
        "updated_at",
    )
    list_filter = ("is_published", "category")
    search_fields = ("slug", "name", "description", "author")
    readonly_fields = ("install_count", "published_at", "updated_at")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(WorkspaceAgentInstall)
class WorkspaceAgentInstallAdmin(admin.ModelAdmin):
    list_display = (
        "workspace",
        "marketplace_agent",
        "automation",
        "installed_by",
        "installed_at",
    )
    list_filter = ("marketplace_agent",)
    search_fields = ("workspace__slug", "marketplace_agent__slug", "automation__name")
    readonly_fields = ("installed_at",)
    autocomplete_fields = ("workspace", "marketplace_agent", "automation", "installed_by")
