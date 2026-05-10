"""ViewSets for workspaces, memberships, and invitations."""

from __future__ import annotations

from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Invitation, Membership, Role, Workspace
from .permissions import IsWorkspaceAdmin, IsWorkspaceMember, IsWorkspaceOwner
from .serializers import (
    CreateInvitationSerializer,
    CreateWorkspaceSerializer,
    InvitationSerializer,
    MembershipSerializer,
    PublicInvitationDetailSerializer,
    UpdateMembershipSerializer,
    WorkspaceSerializer,
)
from .tasks import send_invitation_email


class WorkspaceViewSet(viewsets.ModelViewSet):
    """List + create + retrieve workspaces. List is filtered to user's memberships."""

    serializer_class = WorkspaceSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        if not self.request.user.is_authenticated:
            return Workspace.objects.none()
        return Workspace.objects.filter(
            memberships__user=self.request.user,
            memberships__deactivated_at__isnull=True,
            deleted_at__isnull=True,
        ).distinct()

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        if self.action == "create":
            return CreateWorkspaceSerializer
        return WorkspaceSerializer

    def create(self, request, *args, **kwargs):  # type: ignore[no-untyped-def]
        serializer = CreateWorkspaceSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        workspace = serializer.save()
        # Return the rich representation.
        out = WorkspaceSerializer(workspace, context={"request": request})
        return Response(out.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], permission_classes=[IsWorkspaceOwner])
    def archive(self, request, pk=None):  # type: ignore[no-untyped-def]
        """Soft-delete the workspace. Only the owner of the active workspace can call this,
        and only if the URL pk matches the active workspace."""
        workspace = self.get_object()
        if str(getattr(request, "workspace_id", None)) != str(workspace.pk):
            return Response(
                {"detail": "Archive must target the active workspace (X-Workspace-Id)."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if workspace.deleted_at:
            return Response(
                {"detail": "This workspace is already archived."},
                status=status.HTTP_409_CONFLICT,
            )
        workspace.deleted_at = timezone.now()
        workspace.save(update_fields=["deleted_at"])
        return Response({"id": workspace.pk, "deleted_at": workspace.deleted_at})


class MembershipViewSet(viewsets.ModelViewSet):
    """List memberships for the active workspace; admins can PATCH a role."""

    permission_classes = [IsWorkspaceMember]
    http_method_names = ["get", "patch", "head", "options"]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        workspace_id = getattr(self.request, "workspace_id", None)
        if not workspace_id:
            return Membership.objects.none()
        return (
            Membership.objects.for_workspace(workspace_id)
            .active()
            .select_related("user", "workspace")
        )

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        if self.action in {"update", "partial_update"}:
            return UpdateMembershipSerializer
        return MembershipSerializer

    def get_permissions(self):  # type: ignore[no-untyped-def]
        # Read = any active member; write = admins (owner + admin).
        if self.action in {"update", "partial_update"}:
            return [IsWorkspaceAdmin()]
        return [IsWorkspaceMember()]

    def perform_update(self, serializer):  # type: ignore[no-untyped-def]
        from rest_framework.exceptions import ValidationError

        membership = self.get_object()
        new_role = serializer.validated_data.get("role")
        # Owners can only be modified via a dedicated transfer-ownership flow (post-MVP).
        if membership.role == Role.OWNER:
            raise ValidationError(
                {"detail": "Owners cannot be demoted via PATCH; transfer ownership instead."}
            )
        if new_role == Role.OWNER:
            raise ValidationError(
                {"detail": "Cannot promote to Owner via PATCH; transfer ownership instead."}
            )
        serializer.save()


class InvitationViewSet(viewsets.ModelViewSet):
    """Admins of the active workspace can list, create, and revoke invitations."""

    serializer_class = InvitationSerializer
    permission_classes = [IsWorkspaceAdmin]
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        workspace_id = getattr(self.request, "workspace_id", None)
        if not workspace_id:
            return Invitation.objects.none()
        return (
            Invitation.objects.filter(workspace_id=workspace_id, accepted_at__isnull=True)
            .select_related("workspace", "invited_by")
        )

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        if self.action == "create":
            return CreateInvitationSerializer
        return InvitationSerializer

    def create(self, request, *args, **kwargs):  # type: ignore[no-untyped-def]
        workspace_id = getattr(request, "workspace_id", None)
        serializer = CreateInvitationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invitation = Invitation.objects.create(
            workspace_id=workspace_id,
            invited_by=request.user,
            email=serializer.validated_data["email"],
            role=serializer.validated_data["role"],
        )
        # Send the magic-link email asynchronously.
        accept_url_base = getattr(settings, "INVITE_ACCEPT_URL_BASE", "https://app.offside.ai/accept-invite")
        send_invitation_email.delay(invitation.id, accept_url_base)
        out = InvitationSerializer(invitation)
        return Response(out.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([AllowAny])
def public_invitation_detail(request, token):  # type: ignore[no-untyped-def]
    """Public endpoint — invitee lands here from the magic link to see what they're accepting."""
    invitation = get_object_or_404(Invitation.objects.select_related("workspace", "invited_by"), token=token)
    serializer = PublicInvitationDetailSerializer(invitation)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def accept_invitation(request, token):  # type: ignore[no-untyped-def]
    """Authenticated invitee accepts. Creates the Membership atomically."""
    invitation = get_object_or_404(Invitation, token=token)

    if invitation.is_expired:
        return Response(
            {"detail": "This invitation has expired."},
            status=status.HTTP_410_GONE,
        )
    if invitation.is_accepted:
        return Response(
            {"detail": "This invitation has already been accepted."},
            status=status.HTTP_409_CONFLICT,
        )
    if request.user.email.lower() != invitation.email.lower():
        return Response(
            {"detail": "This invitation was sent to a different email address."},
            status=status.HTTP_403_FORBIDDEN,
        )

    with transaction.atomic():
        membership, created = Membership.objects.get_or_create(
            workspace=invitation.workspace,
            user=request.user,
            defaults={"role": invitation.role},
        )
        invitation.accepted_at = timezone.now()
        invitation.save(update_fields=["accepted_at"])

    return Response(
        {
            "workspace_id": invitation.workspace_id,
            "workspace_slug": invitation.workspace.slug,
            "role": membership.role,
            "created": created,
        },
        status=status.HTTP_200_OK,
    )
