"""AutomationVersion immutability + publish/cancel service tests (M8)."""

from __future__ import annotations

import pytest

from apps.automations.exceptions import GraphError
from apps.automations.models import (
    Automation,
    AutomationRun,
    AutomationStatus,
    AutomationStepRun,
    AutomationVersion,
    RunStatus,
)
from apps.automations.tasks import (
    cancel_run,
    kick_off,
    publish_automation,
    resume_after_hitl,
    run_advancer,
)
from apps.users.models import User
from apps.workspaces.models import Workspace


SIMPLE_GRAPH = {
    "start_node_id": "n1",
    "nodes": {
        "n1": {
            "type": "action",
            "config": {"action": "noop", "input": {"ok": True}},
            "next": "end",
        },
        "end": {"type": "end"},
    },
}


@pytest.fixture
def workspace_user(db):  # type: ignore[no-untyped-def]
    user = User.objects.create_user(email="owner@example.com", password="VerySecurePass123!")
    workspace = Workspace.objects.create(name="Acme", slug="acme", created_by=user)
    return workspace, user


def _draft(workspace, user, graph=None) -> Automation:  # type: ignore[no-untyped-def]
    return Automation.objects.create(
        workspace=workspace,
        name="Draft",
        graph=graph if graph is not None else SIMPLE_GRAPH,
        created_by=user,
    )


@pytest.mark.django_db
def test_publish_creates_version_and_bumps_pointer(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    automation = _draft(workspace, user)
    assert automation.version == 0
    assert automation.published_version is None
    assert automation.status == AutomationStatus.DRAFT

    version = publish_automation(automation, user)
    automation.refresh_from_db()

    assert version.version_number == 1
    assert version.graph == SIMPLE_GRAPH
    assert version.published_by == user
    assert automation.version == 1
    assert automation.published_version_id == version.id
    # First publish flips DRAFT → ACTIVE.
    assert automation.status == AutomationStatus.ACTIVE


@pytest.mark.django_db
def test_publish_rejects_invalid_graph(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    automation = _draft(workspace, user, graph={"nodes": {}})  # missing start_node_id
    with pytest.raises(GraphError):
        publish_automation(automation, user)


@pytest.mark.django_db
def test_second_publish_bumps_version_to_2(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    automation = _draft(workspace, user)
    publish_automation(automation, user)
    automation.refresh_from_db()

    # Edit the draft graph.
    automation.graph = {
        "start_node_id": "n1",
        "nodes": {
            "n1": {
                "type": "action",
                "config": {"action": "noop", "input": {"v": 2}},
                "next": "end",
            },
            "end": {"type": "end"},
        },
    }
    automation.save(update_fields=["graph"])
    v2 = publish_automation(automation, user)
    automation.refresh_from_db()

    assert v2.version_number == 2
    assert automation.version == 2
    assert automation.published_version_id == v2.id
    assert AutomationVersion.objects.filter(automation=automation).count() == 2


@pytest.mark.django_db
def test_in_flight_run_unaffected_by_draft_edit(workspace_user) -> None:  # type: ignore[no-untyped-def]
    """The load-bearing M8 promise: editing a draft graph must NOT change
    the behavior of a run started against an earlier published version.
    """
    workspace, user = workspace_user

    # Build an automation whose v1 graph pauses for approval, then publish.
    pausing_graph = {
        "start_node_id": "n1",
        "nodes": {
            "n1": {
                "type": "approval",
                "config": {"summary": "approve me"},
                "approve_next": "n2",
                "reject_next": "end",
            },
            "n2": {
                "type": "action",
                "config": {"action": "noop", "input": {"v": 1}},
                "next": "end",
            },
            "end": {"type": "end"},
        },
    }
    automation = _draft(workspace, user, graph=pausing_graph)
    v1 = publish_automation(automation, user)

    # Start a run against v1 — it pauses on approval.
    run = AutomationRun.objects.create(
        automation=automation, workspace=workspace, version=v1
    )
    kick_off(run)
    run.refresh_from_db()
    assert run.status == RunStatus.AWAITING_APPROVAL

    # Now mutate the draft graph wildly — the run's behavior must NOT change.
    automation.graph = {
        "start_node_id": "n1",
        "nodes": {
            "n1": {
                "type": "action",
                "config": {"action": "noop", "input": {"v": 99}},
                "next": "end",
            },
            "end": {"type": "end"},
        },
    }
    automation.save(update_fields=["graph"])

    # Resume the existing run — it should still walk the *v1* graph, not the
    # mutated draft.
    resume_after_hitl(run_id=run.pk, decision="approve")
    run.refresh_from_db()

    assert run.status == RunStatus.COMPLETED
    assert run.state_snapshot.get("n2") == {"v": 1}  # v1 graph's value, not 99
    assert run.version_id == v1.id


@pytest.mark.django_db
def test_kick_off_attaches_published_version(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    automation = _draft(workspace, user)
    v1 = publish_automation(automation, user)

    run = AutomationRun.objects.create(automation=automation, workspace=workspace)
    assert run.version_id is None
    kick_off(run)
    run.refresh_from_db()

    assert run.version_id == v1.id
    assert run.status == RunStatus.COMPLETED


@pytest.mark.django_db
def test_kick_off_falls_back_to_draft_graph_for_legacy_runs(workspace_user) -> None:  # type: ignore[no-untyped-def]
    """M7 runs predate AutomationVersion; backward compat must hold."""
    workspace, user = workspace_user
    automation = _draft(workspace, user)  # no publish — pure M7 shape
    run = AutomationRun.objects.create(automation=automation, workspace=workspace)
    kick_off(run)
    run.refresh_from_db()

    assert run.version_id is None
    assert run.status == RunStatus.COMPLETED


@pytest.mark.django_db
def test_kick_off_fails_when_no_published_version_and_empty_draft(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    automation = Automation.objects.create(
        workspace=workspace, name="Empty", graph={}, created_by=user
    )
    run = AutomationRun.objects.create(automation=automation, workspace=workspace)
    kick_off(run)
    run.refresh_from_db()
    assert run.status == RunStatus.FAILED


@pytest.mark.django_db
def test_cancel_run_flips_status(workspace_user) -> None:  # type: ignore[no-untyped-def]
    """TC-32 — cancel a stuck run."""
    workspace, user = workspace_user
    automation = _draft(workspace, user, graph={
        "start_node_id": "n1",
        "nodes": {
            "n1": {"type": "delay", "config": {"seconds": 3600}, "next": "end"},
            "end": {"type": "end"},
        },
    })
    publish_automation(automation, user)
    run = AutomationRun.objects.create(
        automation=automation, workspace=workspace, version=automation.published_version
    )
    kick_off(run)
    run.refresh_from_db()
    assert run.status == RunStatus.AWAITING_DELAY

    cancel_run(run)
    run.refresh_from_db()
    assert run.status == RunStatus.CANCELLED
    assert run.finished_at is not None


@pytest.mark.django_db
def test_cancel_run_is_idempotent_on_terminal(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    automation = _draft(workspace, user)
    publish_automation(automation, user)
    run = AutomationRun.objects.create(
        automation=automation, workspace=workspace, version=automation.published_version
    )
    kick_off(run)
    run.refresh_from_db()
    assert run.status == RunStatus.COMPLETED
    finished_first = run.finished_at

    cancel_run(run)
    run.refresh_from_db()
    # Already terminal — cancel is a no-op.
    assert run.status == RunStatus.COMPLETED
    assert run.finished_at == finished_first
