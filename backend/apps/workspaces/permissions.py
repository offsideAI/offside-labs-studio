"""DRF permissions for workspace-scoped views.

Usage:
    class ContactViewSet(viewsets.ModelViewSet):
        permission_classes = [IsWorkspaceMember]            # any active member
        # or
        permission_classes = [IsWorkspaceManager]           # owner | admin | manager
"""

from __future__ import annotations

from rest_framework.permissions import IsAuthenticated

from .models import Membership, Role


def _has_role(request, allowed: tuple[str, ...]) -> bool:
    workspace_id = getattr(request, "workspace_id", None)
    if not workspace_id or not request.user.is_authenticated:
        return False
    return Membership.objects.filter(
        workspace_id=workspace_id,
        user=request.user,
        role__in=allowed,
        deactivated_at__isnull=True,
    ).exists()


class IsWorkspaceMember(IsAuthenticated):
    """User is authenticated AND has any active membership for the active workspace."""

    def has_permission(self, request, view) -> bool:  # type: ignore[no-untyped-def]
        if not super().has_permission(request, view):
            return False
        return _has_role(
            request,
            (Role.OWNER, Role.ADMIN, Role.MANAGER, Role.REP, Role.READ_ONLY),
        )


class IsWorkspaceOwner(IsAuthenticated):
    def has_permission(self, request, view) -> bool:  # type: ignore[no-untyped-def]
        if not super().has_permission(request, view):
            return False
        return _has_role(request, (Role.OWNER,))


class IsWorkspaceAdmin(IsAuthenticated):
    def has_permission(self, request, view) -> bool:  # type: ignore[no-untyped-def]
        if not super().has_permission(request, view):
            return False
        return _has_role(request, (Role.OWNER, Role.ADMIN))


class IsWorkspaceManager(IsAuthenticated):
    def has_permission(self, request, view) -> bool:  # type: ignore[no-untyped-def]
        if not super().has_permission(request, view):
            return False
        return _has_role(request, (Role.OWNER, Role.ADMIN, Role.MANAGER))
