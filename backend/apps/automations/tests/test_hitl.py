"""HITL pause/resume + token tests."""

from __future__ import annotations

from datetime import timedelta

import jwt
import pytest
from django.conf import settings
from django.utils import timezone

from apps.automations.exceptions import HitlTokenError
from apps.automations.hitl import HITL_TOKEN_PURPOSE, make_token, verify_token
from apps.automations.models import (
    Automation,
    AutomationRun,
    AutomationStatus,
    HitlRequest,
    RunStatus,
)
from apps.automations.tasks import kick_off, resume_after_hitl
from apps.users.models import User
from apps.workspaces.models import Workspace


@pytest.fixture
def workspace_user(db):  # type: ignore[no-untyped-def]
    user = User.objects.create_user(email="owner@example.com", password="VerySecurePass123!")
    workspace = Workspace.objects.create(name="Acme", slug="acme", created_by=user)
    return workspace, user


def test_token_round_trip() -> None:
    token = make_token(hitl_id=42, run_id=7, ttl=timedelta(hours=1))
    payload = verify_token(token)
    assert payload["hitl_id"] == 42
    assert payload["run_id"] == 7
    assert payload["purpose"] == HITL_TOKEN_PURPOSE


def test_expired_token_rejected() -> None:
    token = make_token(hitl_id=1, run_id=1, ttl=timedelta(seconds=-1))
    with pytest.raises(HitlTokenError):
        verify_token(token)


def test_token_with_wrong_purpose_rejected() -> None:
    bad_payload = {
        "purpose": "not-hitl",
        "exp": int((timezone.now() + timedelta(hours=1)).timestamp()),
    }
    bad_token = jwt.encode(bad_payload, settings.SECRET_KEY, algorithm="HS256")
    with pytest.raises(HitlTokenError):
        verify_token(bad_token)


def test_garbage_token_rejected() -> None:
    with pytest.raises(HitlTokenError):
        verify_token("not.a.real.jwt")


@pytest.mark.django_db
def test_approval_step_pauses_run_and_creates_hitl(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    graph = {
        "start_node_id": "n1",
        "nodes": {
            "n1": {
                "type": "approval",
                "config": {"summary": "Approve the test step"},
                "approve_next": "n2",
                "reject_next": "end",
            },
            "n2": {"type": "action", "config": {"action": "noop", "input": {"ok": True}}, "next": "end"},
            "end": {"type": "end"},
        },
    }
    automation = Automation.objects.create(
        workspace=workspace,
        name="Approval test",
        status=AutomationStatus.ACTIVE,
        graph=graph,
        created_by=user,
    )
    run = AutomationRun.objects.create(automation=automation, workspace=workspace)
    kick_off(run)
    run.refresh_from_db()

    assert run.status == RunStatus.AWAITING_APPROVAL
    request = HitlRequest.objects.get(run=run)
    assert request.summary == "Approve the test step"
    assert request.decided_at is None


@pytest.mark.django_db
def test_resume_after_approve_runs_to_completion(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    graph = {
        "start_node_id": "n1",
        "nodes": {
            "n1": {
                "type": "approval",
                "config": {"summary": "approve"},
                "approve_next": "n2",
                "reject_next": "end",
            },
            "n2": {"type": "action", "config": {"action": "noop", "input": {"ok": True}}, "next": "end"},
            "end": {"type": "end"},
        },
    }
    automation = Automation.objects.create(
        workspace=workspace, name="Approve", graph=graph, created_by=user
    )
    run = AutomationRun.objects.create(automation=automation, workspace=workspace)
    kick_off(run)
    run.refresh_from_db()
    assert run.status == RunStatus.AWAITING_APPROVAL

    resume_after_hitl(run_id=run.pk, decision="approve")
    run.refresh_from_db()
    assert run.status == RunStatus.COMPLETED
    assert run.state_snapshot.get("n2") == {"ok": True}


@pytest.mark.django_db
def test_resume_after_reject_routes_to_reject_next(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    graph = {
        "start_node_id": "n1",
        "nodes": {
            "n1": {
                "type": "approval",
                "config": {"summary": "approve"},
                "approve_next": "n2",
                "reject_next": "n3",
            },
            "n2": {"type": "action", "config": {"action": "noop", "input": {"branch": "approved"}}, "next": "end"},
            "n3": {"type": "action", "config": {"action": "noop", "input": {"branch": "rejected"}}, "next": "end"},
            "end": {"type": "end"},
        },
    }
    automation = Automation.objects.create(
        workspace=workspace, name="Reject", graph=graph, created_by=user
    )
    run = AutomationRun.objects.create(automation=automation, workspace=workspace)
    kick_off(run)
    resume_after_hitl(run_id=run.pk, decision="reject")
    run.refresh_from_db()

    assert run.status == RunStatus.COMPLETED
    assert run.state_snapshot.get("n3") == {"branch": "rejected"}
    assert "n2" not in run.state_snapshot
