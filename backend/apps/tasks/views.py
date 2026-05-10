"""ViewSet for tasks."""

from __future__ import annotations

from django.utils import timezone
from rest_framework import viewsets

from apps.workspaces.permissions import IsWorkspaceMember

from .models import Task, TaskStatus
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsWorkspaceMember]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    filterset_fields = ("related_type", "related_id", "status", "owner")

    def get_queryset(self):  # type: ignore[no-untyped-def]
        workspace_id = getattr(self.request, "workspace_id", None)
        if not workspace_id:
            return Task.objects.none()
        qs = (
            Task.objects.for_workspace(workspace_id)
            .filter(deleted_at__isnull=True)
            .select_related("owner")
        )
        params = self.request.query_params
        if related_type := params.get("related_type"):
            qs = qs.filter(related_type=related_type)
        if related_id := params.get("related_id"):
            qs = qs.filter(related_id=related_id)
        if status_param := params.get("status"):
            qs = qs.filter(status=status_param)
        if owner_param := params.get("owner"):
            qs = qs.filter(owner_id=owner_param)
        return qs

    def perform_create(self, serializer):  # type: ignore[no-untyped-def]
        workspace_id = getattr(self.request, "workspace_id", None)
        serializer.save(workspace_id=workspace_id, created_by=self.request.user)

    def perform_update(self, serializer):  # type: ignore[no-untyped-def]
        instance = self.get_object()
        new_status = serializer.validated_data.get("status")
        # Stamp completed_at when transitioning into 'done' for the first time.
        if new_status == TaskStatus.DONE and instance.status != TaskStatus.DONE:
            serializer.save(completed_at=timezone.now())
        elif new_status and new_status != TaskStatus.DONE and instance.completed_at:
            serializer.save(completed_at=None)
        else:
            serializer.save()

    def perform_destroy(self, instance):  # type: ignore[no-untyped-def]
        instance.deleted_at = timezone.now()
        instance.save(update_fields=["deleted_at"])
