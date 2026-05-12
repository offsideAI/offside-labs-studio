"""ViewSets for the automations editor + run inspector (M8)."""

from __future__ import annotations

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.workspaces.permissions import IsWorkspaceManager, IsWorkspaceMember

from .exceptions import GraphError
from .models import (
    Automation,
    AutomationRun,
    AutomationVersion,
)
from .serializers import (
    AutomationRunDetailSerializer,
    AutomationRunSerializer,
    AutomationSerializer,
    AutomationVersionSerializer,
    StartRunSerializer,
)
from .tasks import cancel_run as cancel_run_service
from .tasks import kick_off, publish_automation

from apps.ai.exceptions import AIClientError, AIResponseError
from apps.ai.services import generate_automation_graph


class AutomationViewSet(viewsets.ModelViewSet):
    serializer_class = AutomationSerializer
    permission_classes = [IsWorkspaceMember]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_permissions(self):  # type: ignore[no-untyped-def]
        if self.action in {
            "create",
            "update",
            "partial_update",
            "destroy",
            "publish",
            "start_run",
            "generate_from_nl",
        }:
            return [IsWorkspaceManager()]
        return [IsWorkspaceMember()]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        workspace_id = getattr(self.request, "workspace_id", None)
        if not workspace_id:
            return Automation.objects.none()
        return (
            Automation.objects.for_workspace(workspace_id)
            .select_related("created_by", "published_version")
            .order_by("-created_at")
        )

    def perform_create(self, serializer):  # type: ignore[no-untyped-def]
        workspace_id = getattr(self.request, "workspace_id", None)
        serializer.save(workspace_id=workspace_id, created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):  # type: ignore[no-untyped-def]
        automation = self.get_object()
        try:
            version = publish_automation(automation, request.user)
        except GraphError as exc:
            raise ValidationError({"graph": str(exc)}) from exc
        return Response(
            AutomationVersionSerializer(version).data, status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["get"])
    def versions(self, request, pk=None):  # type: ignore[no-untyped-def]
        automation = self.get_object()
        qs = automation.versions.all().order_by("-version_number")
        page = self.paginate_queryset(qs)
        serializer = AutomationVersionSerializer(page or qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="generate_from_nl")
    def generate_from_nl(self, request, pk=None):  # type: ignore[no-untyped-def]
        """Run the `automations.author_from_nl.v1` Claude prompt and return a
        proposed graph WITHOUT saving. The frontend reviews + commits via PATCH.
        """
        automation = self.get_object()
        description = (request.data.get("description") or "").strip()
        if not description:
            raise ValidationError({"description": "required"})
        workspace_context = (request.data.get("workspace_context") or "").strip()
        try:
            graph, response = generate_automation_graph(
                workspace=automation.workspace,
                description=description,
                requested_by=request.user,
                workspace_context=workspace_context,
            )
        except AIResponseError as exc:
            raise ValidationError({"graph": str(exc)}) from exc
        except AIClientError as exc:
            return Response(
                {"detail": f"AI provider error: {exc}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(
            {
                "graph": graph,
                "model": response.model,
                "tokens_in": response.tokens_in,
                "tokens_out": response.tokens_out,
                "latency_ms": response.latency_ms,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="start_run")
    def start_run(self, request, pk=None):  # type: ignore[no-untyped-def]
        """Manual trigger — kicks off a run using the published version."""
        automation = self.get_object()
        if automation.published_version_id is None:
            raise ValidationError(
                {"detail": "automation has no published version — publish before running"}
            )
        serializer = StartRunSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        run = AutomationRun.objects.create(
            automation=automation,
            workspace=automation.workspace,
            version_id=automation.published_version_id,
            trigger_payload=serializer.validated_data.get("trigger_payload") or {},
        )
        kick_off(run)
        run.refresh_from_db()
        return Response(
            AutomationRunDetailSerializer(run).data, status=status.HTTP_201_CREATED
        )


class AutomationRunViewSet(viewsets.ReadOnlyModelViewSet):
    """Run inspector backend: list / detail + cancel action."""

    permission_classes = [IsWorkspaceMember]

    def get_permissions(self):  # type: ignore[no-untyped-def]
        if self.action == "cancel":
            return [IsWorkspaceManager()]
        return [IsWorkspaceMember()]

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        if self.action == "list":
            return AutomationRunSerializer
        return AutomationRunDetailSerializer

    def get_queryset(self):  # type: ignore[no-untyped-def]
        workspace_id = getattr(self.request, "workspace_id", None)
        if not workspace_id:
            return AutomationRun.objects.none()
        qs = (
            AutomationRun.objects.for_workspace(workspace_id)
            .select_related("automation", "version")
            .prefetch_related("step_runs")
        )
        automation_id = self.request.query_params.get("automation")
        if automation_id:
            qs = qs.filter(automation_id=automation_id)
        run_status = self.request.query_params.get("status")
        if run_status:
            qs = qs.filter(status=run_status)
        return qs

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):  # type: ignore[no-untyped-def]
        run = self.get_object()
        result = cancel_run_service(run)
        run.refresh_from_db()
        return Response(
            {**AutomationRunDetailSerializer(run).data, "cancelled": result == "cancelled"}
        )


class AutomationVersionViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only listing of every published version across an automation.

    Mostly redundant with the nested `/automations/{id}/versions/` action,
    but exposed flat for convenience (e.g. linking from a run inspector page
    straight to the version definition that produced it).
    """

    serializer_class = AutomationVersionSerializer
    permission_classes = [IsWorkspaceMember]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        workspace_id = getattr(self.request, "workspace_id", None)
        if not workspace_id:
            return AutomationVersion.objects.none()
        return AutomationVersion.objects.for_workspace(workspace_id).select_related(
            "automation", "published_by"
        )
