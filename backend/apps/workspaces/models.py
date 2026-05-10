"""Workspace + Membership + Invitation.

Workspace is the tenant boundary. Every workspace-scoped model elsewhere in
the project has a `workspace_id` FK + a `WorkspaceScopedManager`. Roles
gate write operations via `apps.workspaces.permissions`.
"""

from __future__ import annotations

import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from .managers import MembershipManager


class Role(models.TextChoices):
    OWNER = "owner", "Owner"
    ADMIN = "admin", "Admin"
    MANAGER = "manager", "Manager"
    REP = "rep", "Rep"
    READ_ONLY = "read_only", "Read-only"


class Workspace(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=64, unique=True, db_index=True)
    plan = models.CharField(max_length=32, default="free")

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="workspaces_created",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} ({self.slug})"

    @classmethod
    def make_slug(cls, name: str) -> str:
        """Generate a unique slug from a workspace name. Append -2, -3, … on collision."""
        base = slugify(name)[:60] or "workspace"
        slug = base
        counter = 2
        while cls.objects.filter(slug=slug).exists():
            slug = f"{base}-{counter}"[:64]
            counter += 1
        return slug


class Membership(models.Model):
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(max_length=16, choices=Role.choices, default=Role.REP)

    invited_at = models.DateTimeField(default=timezone.now)
    joined_at = models.DateTimeField(default=timezone.now)
    deactivated_at = models.DateTimeField(null=True, blank=True)

    objects: MembershipManager = MembershipManager()

    class Meta:
        ordering = ["-joined_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["workspace", "user"],
                name="unique_workspace_user",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user.email} @ {self.workspace.slug} ({self.role})"


class Invitation(models.Model):
    DEFAULT_TTL = timedelta(days=7)

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="invitations",
    )
    email = models.EmailField()
    role = models.CharField(max_length=16, choices=Role.choices, default=Role.REP)

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)

    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="invitations_sent",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["workspace", "email"]),
        ]

    def __str__(self) -> str:
        return f"{self.email} → {self.workspace.slug} ({self.role})"

    def save(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        if not self.expires_at:
            self.expires_at = timezone.now() + self.DEFAULT_TTL
        super().save(*args, **kwargs)

    @property
    def is_expired(self) -> bool:
        return self.expires_at < timezone.now() if self.expires_at else False

    @property
    def is_accepted(self) -> bool:
        return self.accepted_at is not None
