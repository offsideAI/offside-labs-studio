"""DRF views for the Agents Marketplace (M9.S4 / FR-26).

The catalog (`GET /api/marketplace/agents/` and detail) is anonymously
readable so the marketplace is shareable. `POST .../install/` is the
only mutation, and it requires a workspace + manager role.
"""

from __future__ import annotations

import copy
from typing import Any

from django.db import transaction
from django.db.models import F
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.automations.models import Automation, AutomationStatus
from apps.automations.tasks import publish_automation
from apps.workspaces.authentication import WorkspaceJWTAuthentication
from apps.workspaces.models import Workspace
from apps.workspaces.permissions import IsWorkspaceManager

from .models import MarketplaceAgent, WorkspaceAgentInstall
from .serializers import (
    MarketplaceAgentDetailSerializer,
    MarketplaceAgentListSerializer,
)


class MarketplaceAgentViewSet(viewsets.ReadOnlyModelViewSet):
    """Public catalog browse + workspace-scoped install."""

    queryset = MarketplaceAgent.objects.filter(is_published=True)
    lookup_field = "slug"
    lookup_value_regex = r"[a-zA-Z0-9_-]+"

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        if self.action == "list":
            return MarketplaceAgentListSerializer
        return MarketplaceAgentDetailSerializer

    def get_permissions(self):  # type: ignore[no-untyped-def]
        # Catalog browse is public. Install requires a workspace manager.
        if self.action == "install":
            return [IsWorkspaceManager()]
        return [AllowAny()]

    def get_authenticators(self):  # type: ignore[no-untyped-def]
        # Install uses the workspace-aware JWT auth so we can resolve the
        # active workspace from X-Workspace-Id. Catalog endpoints stay anon.
        if getattr(self, "action", None) == "install":
            return [WorkspaceJWTAuthentication()]
        return []

    def get_queryset(self):  # type: ignore[no-untyped-def]
        qs = super().get_queryset()
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category=category)
        return qs

    @action(detail=True, methods=["post"])
    def install(self, request, slug=None):  # type: ignore[no-untyped-def]
        agent = self.get_object()
        workspace_id = getattr(request, "workspace_id", None)
        if not workspace_id:
            raise ValidationError({"workspace": "missing X-Workspace-Id header"})
        try:
            workspace = Workspace.objects.get(pk=workspace_id)
        except Workspace.DoesNotExist as exc:
            raise ValidationError({"workspace": "workspace not found"}) from exc

        # Seed agents use `"__INSTALLER__"` as a sentinel for fields like
        # `created_by_id` / `author_id` that need to be resolved to a real
        # user at install time. _resolve_installer_sentinels walks the
        # graph + trigger and replaces every literal occurrence with the
        # installing user's pk.
        resolved_graph = _resolve_installer_sentinels(agent.graph, request.user.id)
        resolved_trigger = _resolve_installer_sentinels(agent.trigger, request.user.id)

        with transaction.atomic():
            automation = Automation.objects.create(
                workspace=workspace,
                name=agent.name,
                description=agent.description,
                graph=resolved_graph,
                trigger=resolved_trigger,
                status=AutomationStatus.DRAFT,
                created_by=request.user,
            )
            # publish_automation flips DRAFT → ACTIVE + creates v1.
            version = publish_automation(automation, request.user)
            install = WorkspaceAgentInstall.objects.create(
                workspace=workspace,
                marketplace_agent=agent,
                automation=automation,
                installed_by=request.user,
            )
            MarketplaceAgent.objects.filter(pk=agent.pk).update(
                install_count=F("install_count") + 1
            )

        return Response(
            {
                "automation_id": automation.id,
                "automation_name": automation.name,
                "version_number": version.version_number,
                "install_id": install.id,
            },
            status=status.HTTP_201_CREATED,
        )


_INSTALLER_SENTINEL = "__INSTALLER__"


def _resolve_installer_sentinels(value: Any, installer_id: int) -> Any:
    """Recursively walk a graph/trigger JSON blob, replacing every
    occurrence of the string sentinel `"__INSTALLER__"` with the
    installing user's pk. Leaves all other values untouched.
    """
    if value == _INSTALLER_SENTINEL:
        return installer_id
    if isinstance(value, dict):
        return {k: _resolve_installer_sentinels(v, installer_id) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve_installer_sentinels(v, installer_id) for v in value]
    return value
