"""ImportRun — a single CSV import attempt for a workspace.

The uploaded CSV body is stored on the row (`raw_content`) so the worker
can re-read it. After completion the content can be cleared by a Beat
task; for M4 we keep it for debugging.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.workspaces.managers import WorkspaceScopedManager


class ImportEntityType(models.TextChoices):
    CONTACT = "contact", "Contact"
    COMPANY = "company", "Company"


class ImportStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    RUNNING = "running", "Running"
    COMPLETE = "complete", "Complete"
    FAILED = "failed", "Failed"


class ImportRun(models.Model):
    workspace = models.ForeignKey(
        "workspaces.Workspace",
        on_delete=models.CASCADE,
        related_name="import_runs",
    )
    entity_type = models.CharField(max_length=16, choices=ImportEntityType.choices)
    file_name = models.CharField(max_length=255, blank=True)
    raw_content = models.TextField(blank=True)
    mapping = models.JSONField(default=dict, blank=True)

    status = models.CharField(max_length=16, choices=ImportStatus.choices, default=ImportStatus.PENDING)
    total_rows = models.IntegerField(default=0)
    processed_rows = models.IntegerField(default=0)
    error_rows = models.IntegerField(default=0)
    errors = models.JSONField(default=list, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="import_runs",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    objects = WorkspaceScopedManager()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"ImportRun #{self.pk} ({self.entity_type}, {self.status})"
