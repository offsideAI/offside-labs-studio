"""ViewSet for notes."""

from __future__ import annotations

from django.utils import timezone
from rest_framework import viewsets

from apps.workspaces.permissions import IsWorkspaceMember

from .models import Note
from .serializers import NoteSerializer


class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = [IsWorkspaceMember]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        workspace_id = getattr(self.request, "workspace_id", None)
        if not workspace_id:
            return Note.objects.none()
        qs = (
            Note.objects.for_workspace(workspace_id)
            .filter(deleted_at__isnull=True)
            .select_related("author")
        )
        params = self.request.query_params
        if related_type := params.get("related_type"):
            qs = qs.filter(related_type=related_type)
        if related_id := params.get("related_id"):
            qs = qs.filter(related_id=related_id)
        return qs

    def perform_create(self, serializer):  # type: ignore[no-untyped-def]
        workspace_id = getattr(self.request, "workspace_id", None)
        serializer.save(workspace_id=workspace_id, author=self.request.user)

    def perform_update(self, serializer):  # type: ignore[no-untyped-def]
        instance = self.get_object()
        new_body = serializer.validated_data.get("body_md")
        # Audit edits past the 24h window so we have a paper trail.
        if (
            new_body is not None
            and new_body != instance.body_md
            and not instance.is_within_edit_window
        ):
            log = list(instance.edit_log or [])
            log.append(
                {
                    "edited_at": timezone.now().isoformat(),
                    "edited_by": self.request.user.id,
                    "previous_body_preview": instance.body_md[:200],
                }
            )
            serializer.save(edit_log=log)
        else:
            serializer.save()

    def perform_destroy(self, instance):  # type: ignore[no-untyped-def]
        instance.deleted_at = timezone.now()
        instance.save(update_fields=["deleted_at"])
