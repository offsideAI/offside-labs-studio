"""DRF serializers for the Agents Marketplace (M9.S4 / FR-26)."""

from __future__ import annotations

from rest_framework import serializers

from .models import MarketplaceAgent, WorkspaceAgentInstall


class MarketplaceAgentListSerializer(serializers.ModelSerializer):
    """List representation — omits the full graph for catalog scrolling."""

    class Meta:
        model = MarketplaceAgent
        fields = (
            "id",
            "slug",
            "name",
            "description",
            "category",
            "icon_emoji",
            "author",
            "install_count",
            "published_at",
        )
        read_only_fields = fields


class MarketplaceAgentDetailSerializer(serializers.ModelSerializer):
    """Detail representation — includes graph + trigger so the canvas
    preview can render."""

    class Meta:
        model = MarketplaceAgent
        fields = (
            "id",
            "slug",
            "name",
            "description",
            "long_description",
            "category",
            "icon_emoji",
            "author",
            "graph",
            "trigger",
            "install_count",
            "published_at",
            "updated_at",
        )
        read_only_fields = fields


class WorkspaceAgentInstallSerializer(serializers.ModelSerializer):
    automation_name = serializers.CharField(source="automation.name", read_only=True)
    agent_slug = serializers.SlugField(source="marketplace_agent.slug", read_only=True)
    agent_name = serializers.CharField(source="marketplace_agent.name", read_only=True)

    class Meta:
        model = WorkspaceAgentInstall
        fields = (
            "id",
            "marketplace_agent",
            "agent_slug",
            "agent_name",
            "automation",
            "automation_name",
            "installed_by",
            "installed_at",
        )
        read_only_fields = fields
