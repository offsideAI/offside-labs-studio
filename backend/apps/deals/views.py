"""ViewSets for deals + pipelines."""

from __future__ import annotations

from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.contacts.filters import apply_filter_dsl
from apps.workspaces.permissions import IsWorkspaceManager, IsWorkspaceMember

from .models import Deal, Pipeline
from .serializers import DealSerializer, PipelineSerializer


ALLOWED_DEAL_FIELDS = {
    "id",
    "name",
    "pipeline",
    "stage_id",
    "value_cents",
    "currency",
    "expected_close",
    "contact",
    "company",
    "owner",
    "custom",
    "tags",
    "created_at",
    "updated_at",
}


class PipelineViewSet(viewsets.ModelViewSet):
    serializer_class = PipelineSerializer
    permission_classes = [IsWorkspaceMember]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_permissions(self):  # type: ignore[no-untyped-def]
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsWorkspaceManager()]
        return [IsWorkspaceMember()]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        workspace_id = getattr(self.request, "workspace_id", None)
        if not workspace_id:
            return Pipeline.objects.none()
        return Pipeline.objects.for_workspace(workspace_id)

    def perform_create(self, serializer):  # type: ignore[no-untyped-def]
        workspace_id = getattr(self.request, "workspace_id", None)
        serializer.save(workspace_id=workspace_id, created_by=self.request.user)


class DealViewSet(viewsets.ModelViewSet):
    serializer_class = DealSerializer
    permission_classes = [IsWorkspaceMember]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_permissions(self):  # type: ignore[no-untyped-def]
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsWorkspaceManager()]
        return [IsWorkspaceMember()]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        workspace_id = getattr(self.request, "workspace_id", None)
        if not workspace_id:
            return Deal.objects.none()
        qs = (
            Deal.objects.for_workspace(workspace_id)
            .filter(deleted_at__isnull=True)
            .select_related("pipeline", "contact", "company", "owner")
        )
        try:
            qs = apply_filter_dsl(qs, self.request, ALLOWED_DEAL_FIELDS)
        except ValueError as exc:
            raise ValidationError({"filter": str(exc)}) from exc
        return qs

    def perform_create(self, serializer):  # type: ignore[no-untyped-def]
        workspace_id = getattr(self.request, "workspace_id", None)
        serializer.save(workspace_id=workspace_id, created_by=self.request.user)

    def perform_destroy(self, instance):  # type: ignore[no-untyped-def]
        from django.utils import timezone

        instance.deleted_at = timezone.now()
        instance.save(update_fields=["deleted_at"])
