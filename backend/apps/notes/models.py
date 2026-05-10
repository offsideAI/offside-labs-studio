"""Note — Markdown body attached to any contact / company / deal.

24-hour edit window: edits within 24h are silent. Edits past 24h get
appended to `edit_log` for audit. The frontend warns the user; the
backend permits the edit but records it.
"""

from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.activities.types import RelatedType
from apps.workspaces.managers import WorkspaceScopedManager


NOTE_EDIT_WINDOW = timedelta(hours=24)
NOTE_RELATABLE = {RelatedType.CONTACT, RelatedType.COMPANY, RelatedType.DEAL}


class Note(models.Model):
    workspace = models.ForeignKey(
        "workspaces.Workspace",
        on_delete=models.CASCADE,
        related_name="notes",
    )
    body_md = models.TextField()

    related_type = models.CharField(max_length=16, choices=RelatedType.choices)
    related_id = models.BigIntegerField()

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="notes_authored",
    )

    edit_log = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = WorkspaceScopedManager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["workspace", "related_type", "related_id"]),
        ]

    def __str__(self) -> str:
        return self.body_md[:80]

    @property
    def is_within_edit_window(self) -> bool:
        return timezone.now() - self.created_at <= NOTE_EDIT_WINDOW
