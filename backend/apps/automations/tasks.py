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
    AutomationRun,
    AutomationStepRun,
    HitlRequest,
    PARKED_STATUSES,
    RunStatus,
    StepRunStatus,
)

log = logging.getLogger("apps.automations.runtime")


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

        # Transition PENDING → RUNNING on first advance.
        if run.status == RunStatus.PENDING:
            run.status = RunStatus.RUNNING
            run.started_at = run.started_at or timezone.now()

        # Capture the Celery task id for traceability.
        run.advancer_task_id = (self.request.id or "")[:64]

        # Determine the current node.
        try:
            if not run.current_step_id:
                run.current_step_id = graph.start_node_id(run.automation.graph)
            node = graph.get_node(run.automation.graph, run.current_step_id)
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


def kick_off(run: AutomationRun) -> AutomationRun:
    """Mark a run as PENDING and enqueue the first advancer.

    Used by views, signals, and tests. Idempotent w.r.t. status.
    """
    if run.status not in {RunStatus.PENDING, RunStatus.RUNNING}:
        run.status = RunStatus.PENDING
        run.save(update_fields=["status"])
    run_advancer.delay(run.pk)
    return run


def resume_after_hitl(*, run_id: int, decision: str) -> str:
    """Called by the HITL approval endpoint after the user decides.

    PARKED_STATUSES guards against double-deciding a non-paused run.
    """
    with transaction.atomic():
        run = AutomationRun.objects.select_for_update().get(pk=run_id)
        if run.status != RunStatus.AWAITING_APPROVAL:
            return run.status

        node = graph.get_node(run.automation.graph, run.current_step_id)
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
    "kick_off",
    "resume_after_hitl",
    "PARKED_STATUSES",
]
