"""Deal + Pipeline models.

A Pipeline owns an ordered list of Stage dicts as JSONB. Deals reference
the Pipeline plus a stage_id (string slug). This avoids a separate Stage
table and lets users reorder/rename stages without migrations.

Stage schema:
  {"id": "discovery", "label": "Discovery", "order": 1}
"""

from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.workspaces.managers import WorkspaceScopedManager


def default_pipeline_stages() -> list[dict[str, object]]:
    return [
        {"id": "lead", "label": "Lead", "order": 1},
        {"id": "qualified", "label": "Qualified", "order": 2},
        {"id": "demo", "label": "Demo", "order": 3},
        {"id": "negotiation", "label": "Negotiation", "order": 4},
        {"id": "closed_won", "label": "Closed Won", "order": 5},
        {"id": "closed_lost", "label": "Closed Lost", "order": 6},
    ]


class Pipeline(models.Model):
    workspace = models.ForeignKey(
        "workspaces.Workspace",
        on_delete=models.CASCADE,
        related_name="pipelines",
    )
    name = models.CharField(max_length=120)
    stages = models.JSONField(default=default_pipeline_stages, blank=True)
    is_default = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="pipelines_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = WorkspaceScopedManager()

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["workspace", "name"],
                name="unique_workspace_pipeline_name",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class Deal(models.Model):
    workspace = models.ForeignKey(
        "workspaces.Workspace",
        on_delete=models.CASCADE,
        related_name="deals",
    )
    name = models.CharField(max_length=200)
    pipeline = models.ForeignKey(
        Pipeline,
        on_delete=models.PROTECT,
        related_name="deals",
    )
    stage_id = models.CharField(max_length=64, db_index=True)
    value_cents = models.BigIntegerField(default=0)
    currency = models.CharField(max_length=3, default="USD")
    expected_close = models.DateField(null=True, blank=True)

    contact = models.ForeignKey(
        "contacts.Contact",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deals",
    )
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deals",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_deals",
    )

    custom = models.JSONField(default=dict, blank=True)
    tags = models.JSONField(default=list, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="deals_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = WorkspaceScopedManager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["workspace", "pipeline", "stage_id"]),
            models.Index(fields=["workspace", "owner"]),
        ]

    def __str__(self) -> str:
        return self.name
