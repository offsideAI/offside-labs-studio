"""Happy-path runtime tests for the workflow advancer.

Celery is configured in eager mode in `backend/conftest.py`, so
`run_advancer.delay()` runs synchronously and we can assert on the
post-run state without sleeping or polling.
"""

from __future__ import annotations

import pytest

from apps.automations import actions
from apps.automations.graph import resolve_template
from apps.automations.models import (
    Automation,
    AutomationRun,
    AutomationStepRun,
    AutomationStatus,
    RunStatus,
    StepRunStatus,
)
from apps.automations.tasks import kick_off
from apps.users.models import User
from apps.workspaces.models import Workspace


@pytest.fixture
def workspace_user(db):  # type: ignore[no-untyped-def]
    user = User.objects.create_user(email="owner@example.com", password="VerySecurePass123!")
    workspace = Workspace.objects.create(name="Acme", slug="acme", created_by=user)
    return workspace, user


def _make_automation(workspace, user, graph: dict) -> Automation:  # type: ignore[no-untyped-def]
    return Automation.objects.create(
        workspace=workspace,
        name="Test automation",
        status=AutomationStatus.ACTIVE,
        trigger={"type": "manual"},
        graph=graph,
        created_by=user,
    )


@pytest.mark.django_db
def test_two_step_action_chain_completes(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    graph = {
        "start_node_id": "n1",
        "nodes": {
            "n1": {
                "type": "action",
                "config": {"action": "noop", "input": {"hello": "world"}},
                "next": "n2",
            },
            "n2": {
                "type": "action",
                "config": {"action": "noop", "input": {"piped": "{{ n1.hello }}"}},
                "next": "end",
            },
            "end": {"type": "end"},
        },
    }
    automation = _make_automation(workspace, user, graph)
    run = AutomationRun.objects.create(automation=automation, workspace=workspace)

    kick_off(run)
    run.refresh_from_db()

    assert run.status == RunStatus.COMPLETED
    assert run.finished_at is not None
    assert run.state_snapshot["n1"] == {"hello": "world"}
    assert run.state_snapshot["n2"] == {"piped": "world"}

    step_runs = list(AutomationStepRun.objects.filter(run=run).order_by("id"))
    assert [s.step_id for s in step_runs] == ["n1", "n2"]
    assert all(s.status == StepRunStatus.COMPLETED for s in step_runs)


@pytest.mark.django_db
def test_branch_routes_on_state(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    graph = {
        "start_node_id": "n1",
        "nodes": {
            "n1": {
                "type": "action",
                "config": {"action": "noop", "input": {"score": 90}},
                "next": "n2",
            },
            "n2": {
                "type": "branch",
                "config": {"field": "n1.score", "op": "gt", "value": 70},
                "true_next": "n3",
                "false_next": "n4",
            },
            "n3": {
                "type": "action",
                "config": {"action": "noop", "input": {"branch": "high"}},
                "next": "end",
            },
            "n4": {
                "type": "action",
                "config": {"action": "noop", "input": {"branch": "low"}},
                "next": "end",
            },
            "end": {"type": "end"},
        },
    }
    automation = _make_automation(workspace, user, graph)
    run = AutomationRun.objects.create(automation=automation, workspace=workspace)
    kick_off(run)
    run.refresh_from_db()

    assert run.status == RunStatus.COMPLETED
    assert run.state_snapshot["n3"] == {"branch": "high"}
    assert "n4" not in run.state_snapshot


@pytest.mark.django_db
def test_delay_node_parks_run(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    graph = {
        "start_node_id": "n1",
        "nodes": {
            "n1": {"type": "delay", "config": {"seconds": 60}, "next": "n2"},
            "n2": {"type": "action", "config": {"action": "noop", "input": {}}, "next": "end"},
            "end": {"type": "end"},
        },
    }
    automation = _make_automation(workspace, user, graph)
    run = AutomationRun.objects.create(automation=automation, workspace=workspace)
    kick_off(run)
    run.refresh_from_db()

    assert run.status == RunStatus.AWAITING_DELAY
    assert run.resume_at is not None
    assert run.current_step_id == "n2"  # next node, ready to fire after wake-up


@pytest.mark.django_db
def test_unknown_action_fails_run(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    graph = {
        "start_node_id": "n1",
        "nodes": {
            "n1": {"type": "action", "config": {"action": "no.such.action"}, "next": "end"},
            "end": {"type": "end"},
        },
    }
    automation = _make_automation(workspace, user, graph)
    run = AutomationRun.objects.create(automation=automation, workspace=workspace)
    kick_off(run)
    run.refresh_from_db()

    assert run.status == RunStatus.FAILED
    step = AutomationStepRun.objects.get(run=run, step_id="n1")
    assert step.status == StepRunStatus.FAILED
    assert step.error and "no.such.action" in step.error["message"]


def test_template_resolves_nested() -> None:
    state = {"n1": {"contact": {"id": 42}}}
    assert resolve_template({"id": "{{ n1.contact.id }}"}, state) == {"id": 42}


def test_action_registry_has_builtins() -> None:
    assert "noop" in actions.all_names()
    assert "log" in actions.all_names()
    assert "crm.create_contact" in actions.all_names()
    assert "crm.move_deal_stage" in actions.all_names()
