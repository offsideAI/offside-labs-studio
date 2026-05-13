"""Workflow runtime — `run_advancer` Celery task + Beat wake-up sweep.

The advancer is the heart of the durable runtime. It:
  1. Locks the run row (SELECT FOR UPDATE) inside a transaction.
  2. Resolves the next node from the graph.
  3. For action nodes — calls the handler with an idempotency key. The
     AutomationStepRun row is the durable receipt; replay short-circuits
     to the cached output when it exists.
  4. Persists state in the same transaction.
  5. Re-enqueues itself if the run is still RUNNING, otherwise parks.

Crash safety: a worker that dies mid-step leaves the AutomationStepRun
in either RUNNING or COMPLETED. On replay (Celery resends the task) the
advancer sees the existing row and skips the side effect. See
test_idempotency.py for the chaos demo.
"""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from . import actions, graph
from .exceptions import ActionError, GraphError, WorkflowError
from .hitl import DEFAULT_TTL, make_token
from .models import (
    Automation,
    AutomationRun,
    AutomationStepRun,
    AutomationStatus,
    AutomationVersion,
    HitlRequest,
    PARKED_STATUSES,
    RunStatus,
    ScheduleTrigger,
    StepRunStatus,
    TERMINAL_STATUSES,
)

log = logging.getLogger("apps.automations.runtime")


def _graph_for(run: AutomationRun) -> dict:
    """The frozen graph a run is bound to (falls back to draft for legacy runs)."""
    if run.version_id:
        return run.version.graph
    return run.automation.graph


@shared_task(name="automations.run_advancer", bind=True, max_retries=3)
def run_advancer(self, run_id: int) -> str:  # type: ignore[no-untyped-def]
    """Advance one step of the run. Returns the resulting status."""
    with transaction.atomic():
        try:
            run = AutomationRun.objects.select_for_update().get(pk=run_id)
        except AutomationRun.DoesNotExist:
            log.warning("run_advancer: run %s not found", run_id)
            return RunStatus.FAILED

        # Already terminal or parked — nothing to do.
        if run.status not in (RunStatus.PENDING, RunStatus.RUNNING):
            return run.status

        # Transition PENDING → RUNNING on first advance. Seed the
        # state_snapshot with `{trigger: trigger_payload}` so step input
        # templates can resolve `{{ trigger.<field> }}` (added in
        # M9.S1 / M9.S4 for record + marketplace agents).
        if run.status == RunStatus.PENDING:
            run.status = RunStatus.RUNNING
            run.started_at = run.started_at or timezone.now()
            if "trigger" not in (run.state_snapshot or {}):
                state = dict(run.state_snapshot or {})
                state["trigger"] = run.trigger_payload or {}
                run.state_snapshot = state

        # Capture the Celery task id for traceability.
        run.advancer_task_id = (self.request.id or "")[:64]

        # Determine the current node from the version-frozen graph.
        try:
            run_graph = _graph_for(run)
            if not run.current_step_id:
                run.current_step_id = graph.start_node_id(run_graph)
            node = graph.get_node(run_graph, run.current_step_id)
        except GraphError as exc:
            return _fail_run(run, "GraphError", str(exc))

        run.save()

        node_type = node.get("type")
        config = node.get("config") or {}
        next_id: str | None = node.get("next")

        if node_type == "end":
            run.status = RunStatus.COMPLETED
            run.finished_at = timezone.now()
            run.save(update_fields=["status", "finished_at"])
            return RunStatus.COMPLETED

        if node_type == "delay":
            seconds = int(config.get("seconds", 0))
            run.status = RunStatus.AWAITING_DELAY
            run.resume_at = timezone.now() + timedelta(seconds=seconds)
            run.current_step_id = next_id or ""
            run.save(update_fields=["status", "resume_at", "current_step_id"])
            return RunStatus.AWAITING_DELAY

        if node_type == "approval":
            ttl_seconds = int(config.get("ttl_seconds", DEFAULT_TTL.total_seconds()))
            request = HitlRequest.objects.create(
                run=run,
                step_id=run.current_step_id,
                summary=str(config.get("summary", f"Approve step {run.current_step_id}")),
                payload=run.state_snapshot,
                expires_at=timezone.now() + timedelta(seconds=ttl_seconds),
            )
            # Pre-mint the token so callers can reach hitl_request.token in
            # tests + email templates without recomputing.
            _ = make_token(hitl_id=request.pk, run_id=run.pk, ttl=timedelta(seconds=ttl_seconds))
            run.status = RunStatus.AWAITING_APPROVAL
            run.save(update_fields=["status"])
            return RunStatus.AWAITING_APPROVAL

        if node_type == "wait_for_event":
            run.status = RunStatus.AWAITING_EVENT
            run.awaiting_event_key = str(config.get("event_key", ""))
            run.current_step_id = next_id or ""
            run.save(update_fields=["status", "awaiting_event_key", "current_step_id"])
            return RunStatus.AWAITING_EVENT

        if node_type == "branch":
            field_path = config.get("field")
            op = str(config.get("op", "eq"))
            value = config.get("value")
            actual = graph._path_get(run.state_snapshot, field_path) if field_path else None
            picked = node.get("true_next") if graph.evaluate_branch(actual, op, value) else node.get(
                "false_next"
            )
            run.current_step_id = picked or ""
            run.save(update_fields=["current_step_id"])
            run_advancer.delay(run.pk)
            return RunStatus.RUNNING

        if node_type == "action":
            return _execute_action_node(run, node, config, next_id)

        return _fail_run(run, "GraphError", f"unknown node type: {node_type!r}")


def _execute_action_node(
    run: AutomationRun, node: dict[str, Any], config: dict[str, Any], next_id: str | None
) -> str:
    action_name = config.get("action")
    if not action_name:
        return _fail_run(run, "ActionError", "action node missing config.action")

    # Resolve `{{ a.b.c }}` references in the input template.
    resolved_input = graph.resolve_template(config.get("input") or {}, run.state_snapshot)

    idempotency_key = f"{run.pk}:{run.current_step_id}:{run.attempt + 1}"

    step_run, created = AutomationStepRun.objects.get_or_create(
        idempotency_key=idempotency_key,
        defaults={
            "run": run,
            "step_id": run.current_step_id,
            "attempt": run.attempt + 1,
            "status": StepRunStatus.RUNNING,
            "started_at": timezone.now(),
            "input": resolved_input,
        },
    )

    if not created and step_run.status == StepRunStatus.COMPLETED:
        # Replay: pick up the previous output and advance.
        log.info("run_advancer: idempotent replay for %s", idempotency_key)
        return _record_action_output(run, node, next_id, step_run.output)

    try:
        handler = actions.get(action_name)
        output = handler(run.workspace, resolved_input) or {}
    except WorkflowError as exc:
        step_run.status = StepRunStatus.FAILED
        step_run.error = {"type": exc.__class__.__name__, "message": str(exc)}
        step_run.finished_at = timezone.now()
        step_run.save(update_fields=["status", "error", "finished_at"])
        return _fail_run(run, exc.__class__.__name__, str(exc))
    except Exception as exc:  # noqa: BLE001 — surface every action failure
        step_run.status = StepRunStatus.FAILED
        step_run.error = {"type": exc.__class__.__name__, "message": str(exc)}
        step_run.finished_at = timezone.now()
        step_run.save(update_fields=["status", "error", "finished_at"])
        return _fail_run(run, exc.__class__.__name__, str(exc))

    step_run.status = StepRunStatus.COMPLETED
    step_run.output = output
    step_run.finished_at = timezone.now()
    step_run.save(update_fields=["status", "output", "finished_at"])

    return _record_action_output(run, node, next_id, output)


def _record_action_output(
    run: AutomationRun, node: dict[str, Any], next_id: str | None, output: dict[str, Any]
) -> str:
    state = dict(run.state_snapshot)
    state[run.current_step_id] = output
    run.state_snapshot = state

    if next_id:
        run.current_step_id = next_id
        run.save(update_fields=["state_snapshot", "current_step_id"])
        run_advancer.delay(run.pk)
        return RunStatus.RUNNING

    run.status = RunStatus.COMPLETED
    run.current_step_id = ""
    run.finished_at = timezone.now()
    run.save(update_fields=["state_snapshot", "current_step_id", "status", "finished_at"])
    return RunStatus.COMPLETED


def _fail_run(run: AutomationRun, error_type: str, message: str) -> str:
    log.error("run_advancer: run %s failed (%s): %s", run.pk, error_type, message)
    run.status = RunStatus.FAILED
    run.finished_at = timezone.now()
    run.save(update_fields=["status", "finished_at"])
    return RunStatus.FAILED


@shared_task(name="automations.wake_up_sweep")
def wake_up_sweep() -> int:
    """Re-enqueue advancers for runs whose `resume_at` has passed.

    Scheduled by Celery Beat every 60 seconds (registered via
    django-celery-beat or the static CELERY_BEAT_SCHEDULE). Returns the
    number of runs woken — useful for telemetry.
    """
    now = timezone.now()
    delayed_run_ids = list(
        AutomationRun.objects.filter(
            status=RunStatus.AWAITING_DELAY,
            resume_at__isnull=False,
            resume_at__lte=now,
        ).values_list("pk", flat=True)
    )
    woken = 0
    for run_id in delayed_run_ids:
        # Re-enter RUNNING so the advancer's status guard passes.
        AutomationRun.objects.filter(pk=run_id, status=RunStatus.AWAITING_DELAY).update(
            status=RunStatus.RUNNING
        )
        run_advancer.delay(run_id)
        woken += 1
    return woken


@shared_task(name="automations.scan_schedule_triggers")
def scan_schedule_triggers() -> int:
    """Walk active ScheduleTrigger rows and fire any whose cron is due.

    Runs on the Beat ticker every 60 seconds (see
    `CELERY_BEAT_SCHEDULE` in `offside_crm.settings.base`). Returns
    the count of triggers evaluated as "due now" — useful for
    telemetry. Note: due triggers stamp `last_fired_at` and bump
    `fire_count` even when the bound automation is paused / has no
    published version, to avoid backlog firing when it un-pauses.
    """
    from celery.schedules import crontab as _crontab

    triggers = list(
        ScheduleTrigger.objects.filter(is_active=True).select_related("automation")
    )
    if not triggers:
        return 0

    fired = 0
    for trigger in triggers:
        try:
            parts = trigger.cron_expression.strip().split()
            if len(parts) != 5:
                raise ValueError(f"cron must have 5 fields, got {len(parts)}")
            cron = _crontab(
                minute=parts[0],
                hour=parts[1],
                day_of_month=parts[2],
                month_of_year=parts[3],
                day_of_week=parts[4],
            )
        except Exception as exc:  # noqa: BLE001 — bad crons must not poison the sweep
            log.warning(
                "scan_schedule_triggers: invalid cron on trigger %s: %s",
                trigger.pk,
                exc,
            )
            continue

        # If the trigger has never fired, anchor "last" to 60s ago so the
        # first sweep after creation evaluates whether the cron just hit.
        anchor = trigger.last_fired_at or (timezone.now() - timedelta(seconds=61))
        is_due, _next = cron.is_due(anchor)
        if not is_due:
            continue

        from .triggers import run_automation_with_payload

        run_automation_with_payload(
            trigger.automation,
            trigger_type="schedule",
            payload={
                "schedule_trigger_id": trigger.pk,
                "cron": trigger.cron_expression,
            },
        )
        ScheduleTrigger.objects.filter(pk=trigger.pk).update(
            last_fired_at=timezone.now(),
            fire_count=trigger.fire_count + 1,
        )
        fired += 1
    return fired


def kick_off(run: AutomationRun) -> AutomationRun:
    """Mark a run as PENDING, attach the published version, enqueue the advancer.

    If `run.version` is unset and the automation has a published version, we
    attach it here so subsequent edits to the draft graph can't change the
    run's behavior. If the automation has no published version *and* no draft
    graph (a brand-new automation with no nodes), the run fails immediately.
    """
    if not run.version_id and run.automation.published_version_id:
        run.version_id = run.automation.published_version_id
        run.save(update_fields=["version"])

    if not run.version_id and not (run.automation.graph or {}).get("nodes"):
        run.status = RunStatus.FAILED
        run.finished_at = timezone.now()
        run.save(update_fields=["status", "finished_at"])
        log.warning("kick_off: automation %s has no published version or draft graph", run.automation_id)
        return run

    if run.status not in {RunStatus.PENDING, RunStatus.RUNNING}:
        run.status = RunStatus.PENDING
        run.save(update_fields=["status"])
    run_advancer.delay(run.pk)
    return run


def publish_automation(automation: Automation, user) -> AutomationVersion:  # type: ignore[no-untyped-def]
    """Snapshot the automation's current draft into a new immutable version.

    Bumps `automation.version` and points `automation.published_version` at
    the snapshot. Flips DRAFT → ACTIVE on first publish. Validates the graph
    before snapshotting; raises GraphError on invalid graphs.
    """
    graph.validate(automation.graph)
    with transaction.atomic():
        a = Automation.objects.select_for_update().get(pk=automation.pk)
        new_number = (a.version or 0) + 1
        version = AutomationVersion.objects.create(
            automation=a,
            workspace=a.workspace,
            version_number=new_number,
            graph=a.graph,
            trigger=a.trigger,
            published_by=user,
        )
        a.published_version = version
        a.version = new_number
        update_fields = ["published_version", "version"]
        if a.status == AutomationStatus.DRAFT:
            a.status = AutomationStatus.ACTIVE
            update_fields.append("status")
        a.save(update_fields=update_fields)
    return version


def cancel_run(run: AutomationRun) -> str:
    """Mark a run as CANCELLED. No-op if already terminal."""
    with transaction.atomic():
        r = AutomationRun.objects.select_for_update().get(pk=run.pk)
        if r.status in TERMINAL_STATUSES:
            return r.status
        r.status = RunStatus.CANCELLED
        r.finished_at = timezone.now()
        r.save(update_fields=["status", "finished_at"])
    return RunStatus.CANCELLED


def resume_after_hitl(*, run_id: int, decision: str) -> str:
    """Called by the HITL approval endpoint after the user decides.

    PARKED_STATUSES guards against double-deciding a non-paused run.
    """
    with transaction.atomic():
        run = AutomationRun.objects.select_for_update().get(pk=run_id)
        if run.status != RunStatus.AWAITING_APPROVAL:
            return run.status

        node = graph.get_node(_graph_for(run), run.current_step_id)
        next_id = node.get("approve_next") if decision == "approve" else node.get("reject_next")

        if not next_id:
            run.status = RunStatus.COMPLETED if decision == "approve" else RunStatus.FAILED
            run.finished_at = timezone.now()
            run.save(update_fields=["status", "finished_at"])
            return run.status

        run.status = RunStatus.RUNNING
        run.current_step_id = next_id
        run.save(update_fields=["status", "current_step_id"])

    run_advancer.delay(run.pk)
    return RunStatus.RUNNING


__all__ = [
    "run_advancer",
    "wake_up_sweep",
    "scan_schedule_triggers",
    "kick_off",
    "resume_after_hitl",
    "publish_automation",
    "cancel_run",
    "PARKED_STATUSES",
]
