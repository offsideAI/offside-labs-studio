"""Read-only ViewSet for activities. The log is append-only; rows are
authored by signal handlers in apps.activities.signals or by the
workflow runtime, never by the API.
"""

from __future__ import annotations

from rest_framework import viewsets

from apps.workspaces.permissions import IsWorkspaceMember

from .models import Activity
from .serializers import ActivitySerializer


class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ActivitySerializer
    permission_classes = [IsWorkspaceMember]
    filterset_fields = ("related_type", "related_id", "kind")

    def get_queryset(self):  # type: ignore[no-untyped-def]
        workspace_id = getattr(self.request, "workspace_id", None)
        if not workspace_id:
            return Activity.objects.none()
        qs = Activity.objects.for_workspace(workspace_id).select_related("actor_user")
        params = self.request.query_params
        if related_type := params.get("related_type"):
            qs = qs.filter(related_type=related_type)
        if related_id := params.get("related_id"):
            qs = qs.filter(related_id=related_id)
        if kind := params.get("kind"):
            qs = qs.filter(kind=kind)
        return qs
