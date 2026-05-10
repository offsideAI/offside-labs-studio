"""ViewSet for contacts."""

from __future__ import annotations

from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.workspaces.permissions import IsWorkspaceManager, IsWorkspaceMember

from .filters import apply_filter_dsl
from .models import Contact
from .serializers import ContactSerializer


ALLOWED_FIELDS = {
    "id",
    "first_name",
    "last_name",
    "primary_email",
    "title",
    "company",
    "owner",
    "lifecycle_stage",
    "source",
    "custom",
    "tags",
    "created_at",
    "updated_at",
}


class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = ContactSerializer
    permission_classes = [IsWorkspaceMember]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_permissions(self):  # type: ignore[no-untyped-def]
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsWorkspaceManager()]
        return [IsWorkspaceMember()]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        workspace_id = getattr(self.request, "workspace_id", None)
        if not workspace_id:
            return Contact.objects.none()
        qs = (
            Contact.objects.for_workspace(workspace_id)
            .filter(deleted_at__isnull=True)
            .select_related("company", "owner")
        )
        try:
            qs = apply_filter_dsl(qs, self.request, ALLOWED_FIELDS)
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
