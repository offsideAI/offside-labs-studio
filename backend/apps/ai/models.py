"""Telemetry model for every AI call (PLAN.md §8, CLAUDE.md conventions).

`AICall` rows are the durable audit trail. Every LLM call — whether
initiated from the workflow editor (`automations.author_from_nl.v1`),
the AI condition trigger, or a run-time action — writes a row here so
M11 can:
  - aggregate per-workspace daily token spend → cost guardrails,
  - surface a cost breakdown in the run inspector,
  - debug provider regressions by replaying failed calls.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.workspaces.managers import WorkspaceScopedManager


class AICallStatus(models.TextChoices):
    SUCCESS = "success", "Success"
    ERROR = "error", "Error"


class AICall(models.Model):
    workspace = models.ForeignKey(
        "workspaces.Workspace",
        on_delete=models.CASCADE,
        related_name="ai_calls",
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_calls",
    )

    prompt_name = models.CharField(max_length=128)
    model = models.CharField(max_length=64)
    status = models.CharField(
        max_length=16, choices=AICallStatus.choices, default=AICallStatus.SUCCESS
    )

    tokens_in = models.IntegerField(default=0)
    tokens_out = models.IntegerField(default=0)
    cost_cents = models.IntegerField(default=0)
    latency_ms = models.IntegerField(default=0)

    # Optional FKs — populated when the call was triggered from a specific
    # run/step (run-time AI actions). NULL for editor-time calls like
    # describe-in-English.
    run = models.ForeignKey(
        "automations.AutomationRun",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_calls",
    )
    step_id = models.CharField(max_length=64, blank=True)

    error = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = WorkspaceScopedManager()

    class Meta:
        ordering = ["-id"]
        indexes = [
            models.Index(fields=["workspace", "prompt_name", "-created_at"]),
            models.Index(fields=["workspace", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.prompt_name} · {self.model} · {self.status}"
