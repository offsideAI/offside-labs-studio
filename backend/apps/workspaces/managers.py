"""Manager utilities for workspace-scoped models.

Every model that has a `workspace_id` FK should expose a manager built on
`WorkspaceScopedManager`. ViewSets call `.for_workspace(active_workspace_id)`
to scope querysets. The active workspace id comes from the request header
(`X-Workspace-Id`) validated by `WorkspaceJWTAuthentication`.
"""

from __future__ import annotations

from django.db import models


class WorkspaceScopedQuerySet(models.QuerySet):
    def for_workspace(self, workspace_id) -> "WorkspaceScopedQuerySet":  # type: ignore[type-arg]
        return self.filter(workspace_id=workspace_id)


WorkspaceScopedManager = models.Manager.from_queryset(WorkspaceScopedQuerySet)


class MembershipQuerySet(WorkspaceScopedQuerySet):
    def active(self) -> "MembershipQuerySet":
        return self.filter(deactivated_at__isnull=True)

    def for_user(self, user) -> "MembershipQuerySet":  # type: ignore[no-untyped-def]
        return self.active().filter(user=user)


MembershipManager = models.Manager.from_queryset(MembershipQuerySet)
