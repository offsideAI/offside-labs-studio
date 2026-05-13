"""Manager utilities for workspace-scoped models.

Every model that has a `workspace_id` FK should expose a manager built on
`WorkspaceScopedManager`. ViewSets call `.for_workspace(active_workspace_id)`
to scope querysets. The active workspace id comes from the request header
(`X-Workspace-Id`) validated by `WorkspaceJWTAuthentication`.

**Migration-safety note.** Django's migration framework deconstructs custom
managers to write them into 0001_initial-style files. Managers created
*directly* by `models.Manager.from_queryset(QS)` get a synthetic class
name like `ManagerFromMembershipQuerySet` that has no stable import path
— deconstruction then errors at migrate-time with:

    ValueError: Could not find manager ManagerFromMembershipQuerySet
    in django.db.models.manager.

The fix per the Django docs is to **subclass** the dynamic result into a
named class with a stable module path. That's why `WorkspaceScopedManager`
and `MembershipManager` below are `class … (models.Manager.from_queryset(
QS)): pass` rather than bare `from_queryset(QS)` assignments.
"""

from __future__ import annotations

from django.db import models


class WorkspaceScopedQuerySet(models.QuerySet):
    def for_workspace(self, workspace_id) -> "WorkspaceScopedQuerySet":  # type: ignore[type-arg]
        return self.filter(workspace_id=workspace_id)


class WorkspaceScopedManager(models.Manager.from_queryset(WorkspaceScopedQuerySet)):
    """Named manager — see migration-safety note in module docstring."""


class MembershipQuerySet(WorkspaceScopedQuerySet):
    def active(self) -> "MembershipQuerySet":
        return self.filter(deactivated_at__isnull=True)

    def for_user(self, user) -> "MembershipQuerySet":  # type: ignore[no-untyped-def]
        return self.active().filter(user=user)


class MembershipManager(models.Manager.from_queryset(MembershipQuerySet)):
    """Named manager — see migration-safety note in module docstring."""
