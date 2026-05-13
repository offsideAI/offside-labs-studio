"""Form trigger tests (M9.S1 phase 2c).

Closes 4 of 5 trigger types (record, webhook, schedule, form). AI
condition defers to M11.

Tests cover:
- Happy path → run fires + audit counters bump.
- Form-encoded payload also lands in trigger_payload (request.data
  fallback when body isn't JSON).
- Rate-limit hit returns 429 + Retry-After header.
- Unknown token → 404.
- Inactive endpoint → 403.
- Paused automation → 409 + no run.
- Workspace isolation (form token in one ws doesn't fire automations
  in another).
"""

from __future__ import annotations

import json
import secrets
from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.automations.models import (
    Automation,
    AutomationRun,
    AutomationStatus,
    FormEndpoint,
    RunStatus,
)
from apps.automations.tasks import publish_automation
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


def _published(workspace, user, *, status_=AutomationStatus.ACTIVE):  # type: ignore[no-untyped-def]
    a = Automation.objects.create(
        workspace=workspace,
        name="FormFlow",
        graph=SIMPLE_GRAPH,
        trigger={"type": "form"},
        created_by=user,
    )
    publish_automation(a, user)
    a.refresh_from_db()
    if a.status != status_:
        a.status = status_
        a.save(update_fields=["status"])
    return a


def _endpoint(
    workspace,
    automation,
    user,
    *,
    is_active: bool = True,
    rate_limit_per_minute: int = 10,
) -> FormEndpoint:
    return FormEndpoint.objects.create(
        workspace=workspace,
        automation=automation,
        token=secrets.token_urlsafe(24),
        is_active=is_active,
        rate_limit_per_minute=rate_limit_per_minute,
        created_by=user,
    )


@pytest.mark.django_db
def test_json_submission_fires_run(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    automation = _published(workspace, user)
    endpoint = _endpoint(workspace, automation, user)

    body = json.dumps({"name": "Ada", "email": "ada@example.com"}).encode("utf-8")
    resp = APIClient().post(
        f"/api/forms/{endpoint.token}/submit/",
        data=body,
        content_type="application/json",
    )
    assert resp.status_code == 200, resp.content
    run_id = resp.json()["run_id"]
    run = AutomationRun.objects.get(pk=run_id)
    assert run.status == RunStatus.COMPLETED
    assert run.trigger_payload["name"] == "Ada"
    assert run.trigger_payload["form_token"] == endpoint.token

    endpoint.refresh_from_db()
    assert endpoint.submission_count == 1
    assert endpoint.last_submission_at is not None


@pytest.mark.django_db
def test_form_encoded_submission_also_fires(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    automation = _published(workspace, user)
    endpoint = _endpoint(workspace, automation, user)

    # APIClient.post with a dict + no content_type → multipart/form-data.
    resp = APIClient().post(
        f"/api/forms/{endpoint.token}/submit/",
        data={"name": "Grace", "email": "grace@example.com"},
    )
    assert resp.status_code == 200, resp.content
    run = AutomationRun.objects.get(pk=resp.json()["run_id"])
    assert run.trigger_payload["name"] == "Grace"


@pytest.mark.django_db
def test_rate_limit_returns_429(workspace_user) -> None:  # type: ignore[no-untyped-def]
    """rate_limit_per_minute=10 → min gap of 6 seconds. Backdate
    last_submission_at to 1s ago and assert the next submission is rejected.
    """
    workspace, user = workspace_user
    automation = _published(workspace, user)
    endpoint = _endpoint(workspace, automation, user, rate_limit_per_minute=10)
    FormEndpoint.objects.filter(pk=endpoint.pk).update(
        last_submission_at=timezone.now() - timedelta(seconds=1)
    )

    resp = APIClient().post(
        f"/api/forms/{endpoint.token}/submit/",
        data=b'{"name":"x"}',
        content_type="application/json",
    )
    assert resp.status_code == 429
    assert "Retry-After" in resp.headers
    assert resp.json()["retry_after_seconds"] >= 1
    assert AutomationRun.objects.filter(automation=automation).count() == 0


@pytest.mark.django_db
def test_rate_limit_clears_after_gap(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    automation = _published(workspace, user)
    endpoint = _endpoint(workspace, automation, user, rate_limit_per_minute=60)
    # 60/min → 1s min gap; backdate by 5 seconds so we're clear.
    FormEndpoint.objects.filter(pk=endpoint.pk).update(
        last_submission_at=timezone.now() - timedelta(seconds=5)
    )

    resp = APIClient().post(
        f"/api/forms/{endpoint.token}/submit/",
        data=b'{"k":"v"}',
        content_type="application/json",
    )
    assert resp.status_code == 200


@pytest.mark.django_db
def test_unknown_token_returns_404(db) -> None:  # type: ignore[no-untyped-def]
    resp = APIClient().post(
        "/api/forms/no-such-token/submit/",
        data=b"{}",
        content_type="application/json",
    )
    assert resp.status_code == 404


@pytest.mark.django_db
def test_inactive_endpoint_returns_403(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    automation = _published(workspace, user)
    endpoint = _endpoint(workspace, automation, user, is_active=False)

    resp = APIClient().post(
        f"/api/forms/{endpoint.token}/submit/",
        data=b"{}",
        content_type="application/json",
    )
    assert resp.status_code == 403


@pytest.mark.django_db
def test_paused_automation_returns_409(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    automation = _published(workspace, user, status_=AutomationStatus.PAUSED)
    endpoint = _endpoint(workspace, automation, user)

    resp = APIClient().post(
        f"/api/forms/{endpoint.token}/submit/",
        data=b"{}",
        content_type="application/json",
    )
    assert resp.status_code == 409
    assert AutomationRun.objects.filter(automation=automation).count() == 0
    endpoint.refresh_from_db()
    # Audit counters NOT bumped on rejected submission (different from schedule).
    assert endpoint.submission_count == 0


@pytest.mark.django_db
def test_workspace_isolation(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    # Same automation+endpoint in this workspace.
    automation = _published(workspace, user)
    endpoint = _endpoint(workspace, automation, user)

    # A different workspace shouldn't be affected by a submission to ours.
    other_user = User.objects.create_user(
        email="other@example.com", password="VerySecurePass123!"
    )
    other_ws = Workspace.objects.create(name="Other", slug="other", created_by=other_user)
    other_auto = _published(other_ws, other_user)

    resp = APIClient().post(
        f"/api/forms/{endpoint.token}/submit/",
        data=b'{"x":1}',
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert AutomationRun.objects.filter(automation=other_auto).count() == 0
    assert AutomationRun.objects.filter(automation=automation).count() == 1
