"""ViewSet for companies."""

from __future__ import annotations

from rest_framework import viewsets

from apps.contacts.filters import apply_filter_dsl
from apps.workspaces.permissions import IsWorkspaceManager, IsWorkspaceMember

from .models import Company
from .serializers import CompanySerializer


ALLOWED_FIELDS = {
    "id",
    "name",
    "domain",
    "size_band",
    "industry",
    "owner",
    "custom",
    "tags",
    "created_at",
    "updated_at",
}


class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    permission_classes = [IsWorkspaceMember]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_permissions(self):  # type: ignore[no-untyped-def]
        # Reads = any active member. Writes = managers and above.
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsWorkspaceManager()]
        return [IsWorkspaceMember()]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        workspace_id = getattr(self.request, "workspace_id", None)
        if not workspace_id:
            return Company.objects.none()
        qs = Company.objects.for_workspace(workspace_id).filter(deleted_at__isnull=True)
        return apply_filter_dsl(qs, self.request, ALLOWED_FIELDS)

    def perform_create(self, serializer):  # type: ignore[no-untyped-def]
        workspace_id = getattr(self.request, "workspace_id", None)
        serializer.save(workspace_id=workspace_id, created_by=self.request.user)

    def perform_destroy(self, instance):  # type: ignore[no-untyped-def]
        from django.utils import timezone

        instance.deleted_at = timezone.now()
        instance.save(update_fields=["deleted_at"])
