"""Activity — append-only event log."""

from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.workspaces.managers import WorkspaceScopedManager

from .types import ActivityKind, ActorKind, RelatedType


class Activity(models.Model):
    workspace = models.ForeignKey(
        "workspaces.Workspace",
        on_delete=models.CASCADE,
        related_name="activities",
    )
    kind = models.CharField(max_length=32, choices=ActivityKind.choices)

    actor_kind = models.CharField(max_length=16, choices=ActorKind.choices, default=ActorKind.USER)
    actor_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities",
    )

    related_type = models.CharField(max_length=16, choices=RelatedType.choices)
    related_id = models.BigIntegerField()

    payload = models.JSONField(default=dict, blank=True)

    occurred_at = models.DateTimeField(auto_now_add=True, db_index=True)

    objects = WorkspaceScopedManager()

    class Meta:
        ordering = ["-occurred_at"]
        indexes = [
            models.Index(fields=["workspace", "related_type", "related_id", "-occurred_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.kind} on {self.related_type}#{self.related_id}"
