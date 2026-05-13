"""Models for the durable workflow runtime (PLAN.md §7).

The `AutomationRun` is the state machine. The `run_advancer` Celery task
in tasks.py owns transitions; views never write directly. Idempotency
keys on AutomationStepRun let us crash mid-step + replay without
double-executing side effects.
"""

from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models

from apps.workspaces.managers import WorkspaceScopedManager


class AutomationStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    ACTIVE = "active", "Active"
    PAUSED = "paused", "Paused"
    ARCHIVED = "archived", "Archived"


class RunStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    RUNNING = "running", "Running"
    AWAITING_APPROVAL = "awaiting_approval", "Awaiting approval"
    AWAITING_DELAY = "awaiting_delay", "Awaiting delay"
    AWAITING_EVENT = "awaiting_event", "Awaiting event"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"


# Statuses where the wake-up sweep / external triggers can move the run forward.
PARKED_STATUSES = {RunStatus.AWAITING_DELAY, RunStatus.AWAITING_EVENT, RunStatus.AWAITING_APPROVAL}
ACTIVE_STATUSES = {RunStatus.PENDING, RunStatus.RUNNING}
TERMINAL_STATUSES = {RunStatus.COMPLETED, RunStatus.FAILED, RunStatus.CANCELLED}


class StepRunStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    RUNNING = "running", "Running"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"


class AgentPolicyMode(models.TextChoices):
    SUGGEST = "suggest", "Suggest"
    APPROVE = "approve", "Approve"
    AUTONOMOUS = "autonomous", "Autonomous"


class HitlDecision(models.TextChoices):
    APPROVE = "approve", "Approve"
    REJECT = "reject", "Reject"


class Automation(models.Model):
    """A workflow definition.

    `graph` + `trigger` here are the mutable **draft**. Publishing snapshots
    them into an immutable `AutomationVersion` and points
    `published_version` at the new row. Runs always reference a specific
    version, so editing a draft never changes the behavior of in-flight runs.
    """

    workspace = models.ForeignKey(
        "workspaces.Workspace",
        on_delete=models.CASCADE,
        related_name="automations",
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=16, choices=AutomationStatus.choices, default=AutomationStatus.DRAFT
    )
    trigger = models.JSONField(default=dict, blank=True)
    graph = models.JSONField(default=dict, blank=True)
    version = models.IntegerField(default=0)

    published_version = models.ForeignKey(
        "AutomationVersion",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="automations_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = WorkspaceScopedManager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["workspace", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} v{self.version}"


class AutomationVersion(models.Model):
    """Immutable snapshot of an automation's graph + trigger at publish time.

    Runs reference one of these (not the parent Automation's mutable
    `graph`) so a workflow can be edited without disturbing in-flight runs.
    """

    automation = models.ForeignKey(
        Automation, on_delete=models.CASCADE, related_name="versions"
    )
    workspace = models.ForeignKey(
        "workspaces.Workspace",
        on_delete=models.CASCADE,
        related_name="automation_versions",
    )
    version_number = models.IntegerField()
    graph = models.JSONField()
    trigger = models.JSONField(default=dict, blank=True)
    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="automation_versions_published",
    )
    published_at = models.DateTimeField(auto_now_add=True)

    objects = WorkspaceScopedManager()

    class Meta:
        ordering = ["-version_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["automation", "version_number"],
                name="unique_automation_version_number",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.automation.name} v{self.version_number}"


class AutomationRun(models.Model):
    automation = models.ForeignKey(
        Automation, on_delete=models.PROTECT, related_name="runs"
    )
    # Nullable for M7 runs that pre-date AutomationVersion. New runs created
    # via `kick_off` attach the Automation's published_version automatically.
    version = models.ForeignKey(
        AutomationVersion,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="runs",
    )
    workspace = models.ForeignKey(
        "workspaces.Workspace",
        on_delete=models.CASCADE,
        related_name="automation_runs",
    )

    status = models.CharField(max_length=24, choices=RunStatus.choices, default=RunStatus.PENDING)
    trigger_payload = models.JSONField(default=dict, blank=True)

    current_step_id = models.CharField(max_length=64, blank=True)
    state_snapshot = models.JSONField(default=dict, blank=True)
    attempt = models.IntegerField(default=0)

    resume_at = models.DateTimeField(null=True, blank=True)
    awaiting_event_key = models.CharField(max_length=255, blank=True)

    advancer_task_id = models.CharField(max_length=64, blank=True)

    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    objects = WorkspaceScopedManager()

    class Meta:
        ordering = ["-id"]
        indexes = [
            models.Index(fields=["workspace", "status"]),
            models.Index(fields=["status", "resume_at"]),  # wake-up sweep
            models.Index(fields=["status", "awaiting_event_key"]),
        ]

    def __str__(self) -> str:
        return f"Run #{self.pk} ({self.status})"


class AutomationStepRun(models.Model):
    run = models.ForeignKey(AutomationRun, on_delete=models.CASCADE, related_name="step_runs")
    step_id = models.CharField(max_length=64)
    attempt = models.IntegerField(default=1)

    status = models.CharField(
        max_length=16, choices=StepRunStatus.choices, default=StepRunStatus.PENDING
    )
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    input = models.JSONField(default=dict, blank=True)
    output = models.JSONField(default=dict, blank=True)
    model = models.CharField(max_length=64, blank=True)
    cost_cents = models.IntegerField(default=0)
    error = models.JSONField(null=True, blank=True)

    # Idempotency key = "{run_id}:{step_id}:{attempt}". Action handlers
    # use it to short-circuit on replay (PLAN.md §7.1).
    idempotency_key = models.CharField(max_length=128, unique=True)

    class Meta:
        ordering = ["-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["run", "step_id", "attempt"],
                name="unique_run_step_attempt",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.run_id}:{self.step_id} ({self.status})"


class HitlRequest(models.Model):
    run = models.ForeignKey(AutomationRun, on_delete=models.CASCADE, related_name="hitl_requests")
    step_id = models.CharField(max_length=64)
    summary = models.TextField()
    payload = models.JSONField(default=dict, blank=True)

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    expires_at = models.DateTimeField()
    decided_at = models.DateTimeField(null=True, blank=True)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hitl_decisions",
    )
    decision = models.CharField(max_length=16, choices=HitlDecision.choices, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["run", "decided_at"]),
        ]

    def __str__(self) -> str:
        return f"HITL run={self.run_id} step={self.step_id}"


class WebhookEndpoint(models.Model):
    """Public webhook URL that fires a specific automation (M9.S1).

    Each row mints a URL-safe `token` (the path component of the public
    `POST /api/webhooks/{token}/` URL) and a `secret` used to verify
    `X-Offside-Signature: sha256=<hex>` over the raw request body.
    `is_active=False` lets an admin disable an endpoint without losing
    the URL — disabled endpoints return 403.
    """

    workspace = models.ForeignKey(
        "workspaces.Workspace",
        on_delete=models.CASCADE,
        related_name="webhook_endpoints",
    )
    automation = models.ForeignKey(
        Automation,
        on_delete=models.CASCADE,
        related_name="webhook_endpoints",
    )

    token = models.CharField(max_length=64, unique=True)
    secret = models.CharField(max_length=128)
    label = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="webhook_endpoints_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_fired_at = models.DateTimeField(null=True, blank=True)
    fire_count = models.IntegerField(default=0)

    objects = WorkspaceScopedManager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["workspace", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"webhook {self.token[:8]}… → automation #{self.automation_id}"


class FormEndpoint(models.Model):
    """Public, unsigned form-submission trigger (M9.S1 phase 2c).

    The user-facing URL is `POST /api/forms/{token}/submit/`. The body
    becomes the run's `trigger_payload`. No HMAC — these are for
    in-product / landing-page forms where the value is the captured
    submission, not authenticated identity. Cheap spam guard: each
    endpoint declares `rate_limit_per_minute` and the view enforces
    a minimum gap of `60 / rate_limit_per_minute` seconds between
    submissions.

    For higher-trust integrations (Stripe, GitHub, etc.) use
    `WebhookEndpoint` instead — that one verifies HMAC.
    """

    workspace = models.ForeignKey(
        "workspaces.Workspace",
        on_delete=models.CASCADE,
        related_name="form_endpoints",
    )
    automation = models.ForeignKey(
        Automation,
        on_delete=models.CASCADE,
        related_name="form_endpoints",
    )

    token = models.CharField(max_length=64, unique=True)
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    rate_limit_per_minute = models.IntegerField(default=10)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="form_endpoints_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_submission_at = models.DateTimeField(null=True, blank=True)
    submission_count = models.IntegerField(default=0)

    objects = WorkspaceScopedManager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["workspace", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"form {self.token[:8]}… → automation #{self.automation_id}"


class ScheduleTrigger(models.Model):
    """Cron-driven trigger that fires a specific automation (M9.S1).

    The Beat scan task `automations.scan_schedule_triggers` runs every
    60 seconds, walks active rows, and uses `celery.schedules.crontab`
    to ask "is this due right now given last_fired_at?". Due rows
    `run_automation_with_payload(automation, trigger_type="schedule")`
    and stamp `last_fired_at`.

    Cron format: standard 5-field — `<minute> <hour> <day_of_month>
    <month> <day_of_week>`. Examples: "0 9 * * MON" (Mondays 9am UTC),
    "*/15 * * * *" (every 15 minutes).

    `last_fired_at` is set on every scan that evaluates the trigger,
    even if no run is created (paused automation, no published
    version) — this prevents backlog firing when an automation is
    re-activated.
    """

    workspace = models.ForeignKey(
        "workspaces.Workspace",
        on_delete=models.CASCADE,
        related_name="schedule_triggers",
    )
    automation = models.ForeignKey(
        Automation,
        on_delete=models.CASCADE,
        related_name="schedule_triggers",
    )

    cron_expression = models.CharField(max_length=128)
    timezone_name = models.CharField(max_length=64, default="UTC")
    label = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)

    last_fired_at = models.DateTimeField(null=True, blank=True)
    fire_count = models.IntegerField(default=0)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="schedule_triggers_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = WorkspaceScopedManager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_active", "last_fired_at"]),
            models.Index(fields=["workspace", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"schedule[{self.cron_expression}] → automation #{self.automation_id}"


class AgentPolicy(models.Model):
    """Per-workspace action-mode mapping (PLAN.md §8.5)."""

    workspace = models.ForeignKey(
        "workspaces.Workspace",
        on_delete=models.CASCADE,
        related_name="agent_policies",
    )
    action_type = models.CharField(max_length=64)
    mode = models.CharField(
        max_length=16, choices=AgentPolicyMode.choices, default=AgentPolicyMode.SUGGEST
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = WorkspaceScopedManager()

    class Meta:
        ordering = ["action_type"]
        constraints = [
            models.UniqueConstraint(
                fields=["workspace", "action_type"],
                name="unique_workspace_agent_policy",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.workspace.slug}::{self.action_type} = {self.mode}"
