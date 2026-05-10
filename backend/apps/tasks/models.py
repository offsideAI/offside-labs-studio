"""Task — polymorphic relation to any contact / company / deal.

Stored as `(related_type, related_id)` enum + ID rather than GenericForeignKey
for index-friendly queries (PLAN.md §6).
"""

from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.activities.types import RelatedType
from apps.workspaces.managers import WorkspaceScopedManager


class TaskStatus(models.TextChoices):
    OPEN = "open", "Open"
    IN_PROGRESS = "in_progress", "In progress"
    DONE = "done", "Done"
    CANCELLED = "cancelled", "Cancelled"


class TaskPriority(models.TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"


# Tasks can attach to a contact, company, or deal (not to other tasks/notes).
TASK_RELATABLE = {RelatedType.CONTACT, RelatedType.COMPANY, RelatedType.DEAL}


class Task(models.Model):
    workspace = models.ForeignKey(
        "workspaces.Workspace",
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_at = models.DateTimeField(null=True, blank=True)

    related_type = models.CharField(max_length=16, choices=RelatedType.choices)
    related_id = models.BigIntegerField()

    status = models.CharField(max_length=16, choices=TaskStatus.choices, default=TaskStatus.OPEN)
    priority = models.CharField(
        max_length=16, choices=TaskPriority.choices, default=TaskPriority.MEDIUM
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_tasks",
    )

    custom = models.JSONField(default=dict, blank=True)

    completed_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="tasks_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = WorkspaceScopedManager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["workspace", "related_type", "related_id"]),
            models.Index(fields=["workspace", "owner", "status"]),
            models.Index(fields=["workspace", "due_at"]),
        ]

    def __str__(self) -> str:
        return self.title
