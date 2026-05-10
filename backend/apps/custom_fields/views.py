"""ViewSet for custom field definitions."""

from __future__ import annotations

from rest_framework import viewsets

from apps.workspaces.permissions import IsWorkspaceAdmin, IsWorkspaceMember

from .models import CustomFieldDef
from .serializers import CustomFieldDefSerializer


class CustomFieldDefViewSet(viewsets.ModelViewSet):
    serializer_class = CustomFieldDefSerializer
    permission_classes = [IsWorkspaceMember]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filterset_fields = ("entity_type",)

    def get_permissions(self):  # type: ignore[no-untyped-def]
        # Reads = any active member. Writes = admins.
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsWorkspaceAdmin()]
        return [IsWorkspaceMember()]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        workspace_id = getattr(self.request, "workspace_id", None)
        if not workspace_id:
            return CustomFieldDef.objects.none()
        qs = CustomFieldDef.objects.for_workspace(workspace_id)
        if entity_type := self.request.query_params.get("entity_type"):
            qs = qs.filter(entity_type=entity_type)
        return qs

    def perform_create(self, serializer):  # type: ignore[no-untyped-def]
        workspace_id = getattr(self.request, "workspace_id", None)
        serializer.save(workspace_id=workspace_id)
