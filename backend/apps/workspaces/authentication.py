"""Custom JWT authentication that resolves the active workspace from the X-Workspace-Id header.

Pattern: clients send the active workspace as a header, not as a JWT claim. This
makes workspace switching cheap (no token rotation) and keeps the JWT minimal.
The header value is validated against the user's active memberships before being
attached to `request.workspace_id`.
"""

from __future__ import annotations

from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Membership

WORKSPACE_HEADER = "HTTP_X_WORKSPACE_ID"


class WorkspaceJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):  # type: ignore[no-untyped-def]
        result = super().authenticate(request)
        if result is None:
            request.workspace_id = None
            return None
        user, validated_token = result
        request.workspace_id = self._resolve_workspace_id(request, user)
        return result

    @staticmethod
    def _resolve_workspace_id(request, user):  # type: ignore[no-untyped-def]
        header_value = request.META.get(WORKSPACE_HEADER)
        if not header_value:
            return None
        try:
            workspace_id = int(header_value)
        except (ValueError, TypeError):
            return None
        if Membership.objects.filter(
            workspace_id=workspace_id,
            user=user,
            deactivated_at__isnull=True,
        ).exists():
            return workspace_id
        return None
