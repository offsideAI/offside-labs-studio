"""Webhook trigger tests (M9.S1 phase 2a).

Covers:
- Valid HMAC → fires the bound automation + run completes.
- `sha256=` prefix and bare-hex signatures both accepted.
- Bad signature → 401, no run created.
- Unknown token → 404.
- Inactive endpoint → 403.
- Inactive automation (DRAFT, or no published version) → 409.
- fire_count + last_fired_at are bumped on success.
- Non-JSON body still fires the run with a fallback payload.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets

import pytest
from rest_framework.test import APIClient

from apps.automations.models import (
    Automation,
    AutomationRun,
    AutomationStatus,
    RunStatus,
    WebhookEndpoint,
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
        name="WebhookFlow",
        graph=SIMPLE_GRAPH,
        trigger={"type": "webhook"},
        created_by=user,
    )
    publish_automation(a, user)
    a.refresh_from_db()
    if a.status != status_:
        a.status = status_
        a.save(update_fields=["status"])
    return a


def _endpoint(workspace, automation, user, *, is_active=True):  # type: ignore[no-untyped-def]
    return WebhookEndpoint.objects.create(
        workspace=workspace,
        automation=automation,
        token=secrets.token_urlsafe(24),
        secret=secrets.token_hex(32),
        is_active=is_active,
        created_by=user,
    )


def _sign(secret: str, body: bytes, *, prefix: bool = True) -> str:
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}" if prefix else digest


@pytest.mark.django_db
def test_valid_signature_fires_run(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    automation = _published(workspace, user)
    endpoint = _endpoint(workspace, automation, user)

    client = APIClient()
    body = json.dumps({"hello": "world", "score": 42}).encode("utf-8")
    sig = _sign(endpoint.secret, body)

    resp = client.post(
        f"/api/webhooks/{endpoint.token}/",
        data=body,
        content_type="application/json",
        HTTP_X_OFFSIDE_SIGNATURE=sig,
    )
    assert resp.status_code == 200, resp.content
    run_id = resp.json()["run_id"]
    run = AutomationRun.objects.get(pk=run_id)
    assert run.automation_id == automation.id
    assert run.version_id == automation.published_version_id
    assert run.status == RunStatus.COMPLETED
    assert run.trigger_payload["hello"] == "world"
    assert run.trigger_payload["type"] == "webhook"
    assert run.trigger_payload["webhook_token"] == endpoint.token

    endpoint.refresh_from_db()
    assert endpoint.fire_count == 1
    assert endpoint.last_fired_at is not None


@pytest.mark.django_db
def test_bare_hex_signature_accepted(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    automation = _published(workspace, user)
    endpoint = _endpoint(workspace, automation, user)

    client = APIClient()
    body = b'{"k":"v"}'
    sig = _sign(endpoint.secret, body, prefix=False)

    resp = client.post(
        f"/api/webhooks/{endpoint.token}/",
        data=body,
        content_type="application/json",
        HTTP_X_OFFSIDE_SIGNATURE=sig,
    )
    assert resp.status_code == 200, resp.content


@pytest.mark.django_db
def test_bad_signature_returns_401(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    automation = _published(workspace, user)
    endpoint = _endpoint(workspace, automation, user)

    client = APIClient()
    body = b'{"k":"v"}'

    resp = client.post(
        f"/api/webhooks/{endpoint.token}/",
        data=body,
        content_type="application/json",
        HTTP_X_OFFSIDE_SIGNATURE="sha256=deadbeef",
    )
    assert resp.status_code == 401
    assert AutomationRun.objects.filter(automation=automation).count() == 0


@pytest.mark.django_db
def test_missing_signature_returns_401(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    automation = _published(workspace, user)
    endpoint = _endpoint(workspace, automation, user)

    client = APIClient()
    resp = client.post(
        f"/api/webhooks/{endpoint.token}/",
        data=b"{}",
        content_type="application/json",
    )
    assert resp.status_code == 401


@pytest.mark.django_db
def test_unknown_token_returns_404(db) -> None:  # type: ignore[no-untyped-def]
    client = APIClient()
    resp = client.post(
        "/api/webhooks/no-such-token/",
        data=b"{}",
        content_type="application/json",
        HTTP_X_OFFSIDE_SIGNATURE="sha256=deadbeef",
    )
    assert resp.status_code == 404


@pytest.mark.django_db
def test_inactive_endpoint_returns_403(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    automation = _published(workspace, user)
    endpoint = _endpoint(workspace, automation, user, is_active=False)

    body = b"{}"
    sig = _sign(endpoint.secret, body)
    resp = APIClient().post(
        f"/api/webhooks/{endpoint.token}/",
        data=body,
        content_type="application/json",
        HTTP_X_OFFSIDE_SIGNATURE=sig,
    )
    assert resp.status_code == 403


@pytest.mark.django_db
def test_paused_automation_returns_409(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    automation = _published(workspace, user, status_=AutomationStatus.PAUSED)
    endpoint = _endpoint(workspace, automation, user)

    body = b"{}"
    sig = _sign(endpoint.secret, body)
    resp = APIClient().post(
        f"/api/webhooks/{endpoint.token}/",
        data=body,
        content_type="application/json",
        HTTP_X_OFFSIDE_SIGNATURE=sig,
    )
    assert resp.status_code == 409
    assert AutomationRun.objects.filter(automation=automation).count() == 0


@pytest.mark.django_db
def test_non_json_body_still_fires(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    automation = _published(workspace, user)
    endpoint = _endpoint(workspace, automation, user)

    body = b"this is not JSON, just bytes"
    sig = _sign(endpoint.secret, body)
    resp = APIClient().post(
        f"/api/webhooks/{endpoint.token}/",
        data=body,
        content_type="text/plain",
        HTTP_X_OFFSIDE_SIGNATURE=sig,
    )
    assert resp.status_code == 200
    run = AutomationRun.objects.get(pk=resp.json()["run_id"])
    assert "raw" in run.trigger_payload
