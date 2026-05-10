"""Idempotency / crash-safety tests.

The runtime's load-bearing promise is that a worker dying mid-step
doesn't double-execute side effects on replay. We simulate that by
calling `run_advancer` twice with the same run state, after pre-creating
a COMPLETED AutomationStepRow for the action's idempotency key.
"""

from __future__ import annotations

import pytest

from apps.automations import actions
from apps.automations.models import (
    Automation,
    AutomationRun,
    AutomationStepRun,
    AutomationStatus,
    RunStatus,
    StepRunStatus,
)
from apps.automations.tasks import kick_off, run_advancer, wake_up_sweep
from apps.contacts.models import Contact
from apps.users.models import User
from apps.workspaces.models import Workspace


@pytest.fixture
def workspace_user(db):  # type: ignore[no-untyped-def]
    user = User.objects.create_user(email="owner@example.com", password="VerySecurePass123!")
    workspace = Workspace.objects.create(name="Acme", slug="acme", created_by=user)
    return workspace, user


@pytest.mark.django_db
def test_replay_does_not_double_create_contact(workspace_user) -> None:  # type: ignore[no-untyped-def]
    """Run a `crm.create_contact` action once. Pretend the worker died
    *after* the side effect succeeded — re-running the advancer must
    short-circuit on the cached step output rather than create a second
    contact."""
    workspace, user = workspace_user

    graph = {
        "start_node_id": "n1",
        "nodes": {
            "n1": {
                "type": "action",
                "config": {
                    "action": "crm.create_contact",
                    "input": {
                        "first_name": "Ada",
                        "last_name": "Lovelace",
                        "primary_email": "ada@example.com",
                        "created_by_id": user.id,
                    },
                },
                "next": "end",
            },
            "end": {"type": "end"},
        },
    }
    automation = Automation.objects.create(
        workspace=workspace,
        name="Replay test",
        status=AutomationStatus.ACTIVE,
        graph=graph,
        created_by=user,
    )
    run = AutomationRun.objects.create(automation=automation, workspace=workspace)
    kick_off(run)
    run.refresh_from_db()
    assert run.status == RunStatus.COMPLETED

    initial_count = Contact.objects.filter(workspace=workspace).count()
    assert initial_count == 1

    # Now simulate a Celery resend of the same task: the run is already
    # COMPLETED so the advancer's status guard kicks it out without
    # re-executing the action. Even more importantly, if we manually rewind
    # the run to RUNNING and replay, the idempotency key on
    # AutomationStepRun forces a no-op replay path.
    run.status = RunStatus.RUNNING
    run.current_step_id = "n1"
    run.finished_at = None
    run.save()

    run_advancer.apply(args=[run.pk])
    run.refresh_from_db()

    assert Contact.objects.filter(workspace=workspace).count() == initial_count
    # Run should walk through `n1` (idempotent replay) → end → COMPLETED.
    assert run.status == RunStatus.COMPLETED


@pytest.mark.django_db
def test_idempotency_key_uniqueness_enforced(workspace_user) -> None:  # type: ignore[no-untyped-def]
    """Two AutomationStepRun rows can't share an idempotency key — the
    DB constraint catches a buggy advancer that forgets to look up the
    existing row first."""
    workspace, user = workspace_user
    automation = Automation.objects.create(
        workspace=workspace,
        name="Conflict",
        graph={"start_node_id": "n1", "nodes": {"n1": {"type": "end"}}},
        created_by=user,
    )
    run = AutomationRun.objects.create(automation=automation, workspace=workspace)
    AutomationStepRun.objects.create(
        run=run,
        step_id="n1",
        attempt=1,
        status=StepRunStatus.COMPLETED,
        idempotency_key="test-key",
    )
    with pytest.raises(Exception):
        AutomationStepRun.objects.create(
            run=run,
            step_id="n1",
            attempt=1,
            status=StepRunStatus.RUNNING,
            idempotency_key="test-key",
        )


@pytest.mark.django_db
def test_wake_up_sweep_resumes_delayed_run(workspace_user) -> None:  # type: ignore[no-untyped-def]
    """A run parked in AWAITING_DELAY with resume_at in the past should
    be re-enqueued by the wake-up sweep and run to completion."""
    from datetime import timedelta

    from django.utils import timezone

    workspace, user = workspace_user
    graph = {
        "start_node_id": "n1",
        "nodes": {
            "n1": {"type": "delay", "config": {"seconds": 1}, "next": "n2"},
            "n2": {"type": "action", "config": {"action": "noop", "input": {}}, "next": "end"},
            "end": {"type": "end"},
        },
    }
    automation = Automation.objects.create(
        workspace=workspace, name="Delay", graph=graph, created_by=user
    )
    run = AutomationRun.objects.create(automation=automation, workspace=workspace)
    kick_off(run)
    run.refresh_from_db()
    assert run.status == RunStatus.AWAITING_DELAY

    # Backdate resume_at so the sweep picks it up.
    AutomationRun.objects.filter(pk=run.pk).update(
        resume_at=timezone.now() - timedelta(seconds=5)
    )

    woken = wake_up_sweep.apply().get()
    assert woken == 1

    run.refresh_from_db()
    assert run.status == RunStatus.COMPLETED


def test_action_registry_lookup_for_unknown_raises() -> None:
    from apps.automations.exceptions import ActionError

    with pytest.raises(ActionError):
        actions.get("does.not.exist")
