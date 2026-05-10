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
from .permissions import IsWorkspaceAdmin, IsWorkspaceMember
from .serializers import (
    CreateInvitationSerializer,
    CreateWorkspaceSerializer,
    InvitationSerializer,
    MembershipSerializer,
    PublicInvitationDetailSerializer,
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


class MembershipViewSet(viewsets.ReadOnlyModelViewSet):
    """List memberships for the active workspace."""

    serializer_class = MembershipSerializer
    permission_classes = [IsWorkspaceMember]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        workspace_id = getattr(self.request, "workspace_id", None)
        if not workspace_id:
            return Membership.objects.none()
        return (
            Membership.objects.for_workspace(workspace_id)
            .active()
            .select_related("user", "workspace")
        )


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
