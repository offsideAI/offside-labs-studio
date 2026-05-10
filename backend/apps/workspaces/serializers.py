"""DRF serializers for workspaces, memberships, and invitations."""

from __future__ import annotations

from rest_framework import serializers

from .models import Invitation, Membership, Role, Workspace


class WorkspaceSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = Workspace
        fields = ("id", "name", "slug", "plan", "created_at", "updated_at", "role")
        read_only_fields = ("id", "slug", "plan", "created_at", "updated_at", "role")

    def get_role(self, obj: Workspace) -> str | None:
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        membership = Membership.objects.filter(
            workspace=obj, user=request.user, deactivated_at__isnull=True
        ).first()
        return membership.role if membership else None


class CreateWorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = ("name",)

    def create(self, validated_data: dict) -> Workspace:
        request = self.context["request"]
        name = validated_data["name"]
        workspace = Workspace.objects.create(
            name=name,
            slug=Workspace.make_slug(name),
            created_by=request.user,
        )
        Membership.objects.create(
            workspace=workspace,
            user=request.user,
            role=Role.OWNER,
        )
        return workspace


class MembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_full_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = Membership
        fields = (
            "id",
            "user",
            "user_email",
            "user_full_name",
            "workspace",
            "role",
            "joined_at",
            "deactivated_at",
        )
        read_only_fields = (
            "id",
            "user",
            "user_email",
            "user_full_name",
            "workspace",
            "joined_at",
            "deactivated_at",
        )


class InvitationSerializer(serializers.ModelSerializer):
    invited_by_email = serializers.EmailField(source="invited_by.email", read_only=True)
    workspace_name = serializers.CharField(source="workspace.name", read_only=True)

    class Meta:
        model = Invitation
        fields = (
            "id",
            "email",
            "role",
            "workspace",
            "workspace_name",
            "invited_by",
            "invited_by_email",
            "created_at",
            "expires_at",
            "accepted_at",
        )
        read_only_fields = (
            "id",
            "workspace",
            "workspace_name",
            "invited_by",
            "invited_by_email",
            "created_at",
            "expires_at",
            "accepted_at",
        )


class CreateInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = ("email", "role")

    def validate_role(self, value: str) -> str:
        # Owners cannot be invited — they're created at workspace-creation time.
        if value == Role.OWNER:
            raise serializers.ValidationError("Owners cannot be invited; transfer ownership instead.")
        return value


class PublicInvitationDetailSerializer(serializers.ModelSerializer):
    """Returned to the unauthenticated invitee landing on the magic link."""

    workspace_name = serializers.CharField(source="workspace.name", read_only=True)
    workspace_slug = serializers.CharField(source="workspace.slug", read_only=True)
    invited_by_email = serializers.EmailField(source="invited_by.email", read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    is_accepted = serializers.BooleanField(read_only=True)

    class Meta:
        model = Invitation
        fields = (
            "email",
            "role",
            "workspace_name",
            "workspace_slug",
            "invited_by_email",
            "is_expired",
            "is_accepted",
        )
