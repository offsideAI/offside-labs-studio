"""DRF API tests for the M8 automations editor + run inspector.

Maps to TC-29 (publish a workflow), TC-30 (edit + republish), and TC-32
(cancel a stuck run). TC-31 (NL-to-graph) lives in the frontend.
"""

from __future__ import annotations

import pytest
from allauth.account.models import EmailAddress
from rest_framework import status
from rest_framework.test import APIClient

from apps.automations.models import (
    Automation,
    AutomationRun,
    AutomationStatus,
    AutomationVersion,
    RunStatus,
)
from apps.users.models import User
from apps.workspaces.models import Membership, Role, Workspace


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


def _verified_user(email: str) -> User:
    user = User.objects.create_user(email=email, password="VerySecurePass123!")
    EmailAddress.objects.create(user=user, email=email, verified=True, primary=True)
    return user


def _login(client: APIClient, email: str) -> str:
    resp = client.post(
        "/api/auth/login/",
        {"email": email, "password": "VerySecurePass123!"},
        format="json",
    )
    return resp.json()["access"]


@pytest.fixture
def owner_session(db):  # type: ignore[no-untyped-def]
    user = _verified_user("owner@example.com")
    workspace = Workspace.objects.create(name="Acme", slug="acme", created_by=user)
    Membership.objects.create(workspace=workspace, user=user, role=Role.OWNER)
    client = APIClient()
    access = _login(client, "owner@example.com")
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access}",
        HTTP_X_WORKSPACE_ID=str(workspace.id),
    )
    return client, workspace, user


@pytest.mark.django_db
def test_create_draft_automation(owner_session) -> None:  # type: ignore[no-untyped-def]
    client, _, _ = owner_session
    resp = client.post(
        "/api/automations/",
        {"name": "Welcome flow", "trigger": {"type": "manual"}, "graph": SIMPLE_GRAPH},
        format="json",
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.content
    body = resp.json()
    assert body["status"] == AutomationStatus.DRAFT
    assert body["version"] == 0
    assert body["published_version"] is None


@pytest.mark.django_db
def test_publish_creates_version_and_flips_status(owner_session) -> None:  # type: ignore[no-untyped-def]
    """TC-29 — publish a workflow."""
    client, workspace, user = owner_session
    automation = Automation.objects.create(
        workspace=workspace, name="Pub", graph=SIMPLE_GRAPH, created_by=user
    )

    resp = client.post(f"/api/automations/{automation.id}/publish/", format="json")
    assert resp.status_code == status.HTTP_201_CREATED, resp.content
    body = resp.json()
    assert body["version_number"] == 1
    assert body["graph"] == SIMPLE_GRAPH

    automation.refresh_from_db()
    assert automation.version == 1
    assert automation.status == AutomationStatus.ACTIVE
    assert automation.published_version_id == body["id"]


@pytest.mark.django_db
def test_publish_invalid_graph_returns_400(owner_session) -> None:  # type: ignore[no-untyped-def]
    client, workspace, user = owner_session
    automation = Automation.objects.create(
        workspace=workspace, name="Bad", graph={"nodes": {}}, created_by=user
    )

    resp = client.post(f"/api/automations/{automation.id}/publish/", format="json")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "graph" in resp.json()


@pytest.mark.django_db
def test_edit_and_republish_creates_v2(owner_session) -> None:  # type: ignore[no-untyped-def]
    """TC-30 — edit draft graph + republish → version 2 exists alongside v1."""
    client, workspace, user = owner_session
    automation = Automation.objects.create(
        workspace=workspace, name="EvolvingFlow", graph=SIMPLE_GRAPH, created_by=user
    )
    client.post(f"/api/automations/{automation.id}/publish/", format="json")

    edited_graph = {
        "start_node_id": "n1",
        "nodes": {
            "n1": {
                "type": "action",
                "config": {"action": "log", "input": {"msg": "hi"}},
                "next": "end",
            },
            "end": {"type": "end"},
        },
    }
    patch = client.patch(
        f"/api/automations/{automation.id}/",
        {"graph": edited_graph},
        format="json",
    )
    assert patch.status_code == status.HTTP_200_OK, patch.content

    pub2 = client.post(f"/api/automations/{automation.id}/publish/", format="json")
    assert pub2.status_code == status.HTTP_201_CREATED
    assert pub2.json()["version_number"] == 2

    listing = client.get(f"/api/automations/{automation.id}/versions/")
    assert listing.status_code == status.HTTP_200_OK
    page = listing.json()
    versions = page.get("results", page) if isinstance(page, dict) else page
    numbers = [v["version_number"] for v in versions]
    assert numbers == [2, 1]


@pytest.mark.django_db
def test_start_run_requires_published_version(owner_session) -> None:  # type: ignore[no-untyped-def]
    client, workspace, user = owner_session
    automation = Automation.objects.create(
        workspace=workspace, name="Unpub", graph=SIMPLE_GRAPH, created_by=user
    )
    resp = client.post(f"/api/automations/{automation.id}/start_run/", format="json")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_start_run_creates_run_against_published_version(owner_session) -> None:  # type: ignore[no-untyped-def]
    client, workspace, user = owner_session
    automation = Automation.objects.create(
        workspace=workspace, name="Runnable", graph=SIMPLE_GRAPH, created_by=user
    )
    pub = client.post(f"/api/automations/{automation.id}/publish/", format="json").json()

    resp = client.post(
        f"/api/automations/{automation.id}/start_run/",
        {"trigger_payload": {"hello": "world"}},
        format="json",
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.content
    body = resp.json()
    assert body["version"] == pub["id"]
    assert body["status"] == RunStatus.COMPLETED
    assert body["trigger_payload"] == {"hello": "world"}
    # Step rows are inlined for the inspector.
    step_runs = body["step_runs"]
    assert [s["step_id"] for s in step_runs] == ["n1"]


@pytest.mark.django_db
def test_cancel_run_endpoint(owner_session) -> None:  # type: ignore[no-untyped-def]
    """TC-32 — cancel a stuck run."""
    client, workspace, user = owner_session
    automation = Automation.objects.create(
        workspace=workspace,
        name="Stuck",
        graph={
            "start_node_id": "n1",
            "nodes": {
                "n1": {"type": "delay", "config": {"seconds": 3600}, "next": "end"},
                "end": {"type": "end"},
            },
        },
        created_by=user,
    )
    client.post(f"/api/automations/{automation.id}/publish/", format="json")
    started = client.post(
        f"/api/automations/{automation.id}/start_run/", format="json"
    ).json()
    assert started["status"] == RunStatus.AWAITING_DELAY

    resp = client.post(f"/api/automation-runs/{started['id']}/cancel/", format="json")
    assert resp.status_code == status.HTTP_200_OK, resp.content
    body = resp.json()
    assert body["status"] == RunStatus.CANCELLED
    assert body["cancelled"] is True


@pytest.mark.django_db
def test_run_detail_includes_step_runs(owner_session) -> None:  # type: ignore[no-untyped-def]
    client, workspace, user = owner_session
    automation = Automation.objects.create(
        workspace=workspace, name="Inspect", graph=SIMPLE_GRAPH, created_by=user
    )
    client.post(f"/api/automations/{automation.id}/publish/", format="json")
    run_body = client.post(
        f"/api/automations/{automation.id}/start_run/", format="json"
    ).json()

    resp = client.get(f"/api/automation-runs/{run_body['id']}/")
    assert resp.status_code == status.HTTP_200_OK
    body = resp.json()
    assert "step_runs" in body
    assert body["state_snapshot"] == {"n1": {"ok": True}}


@pytest.mark.django_db
def test_workspace_isolation_on_automations(owner_session) -> None:  # type: ignore[no-untyped-def]
    client, _, _ = owner_session

    # Build a second workspace + owner, create an automation there.
    other_user = _verified_user("other@example.com")
    other_ws = Workspace.objects.create(name="Other", slug="other", created_by=other_user)
    Membership.objects.create(workspace=other_ws, user=other_user, role=Role.OWNER)
    other_auto = Automation.objects.create(
        workspace=other_ws, name="Isolated", graph=SIMPLE_GRAPH, created_by=other_user
    )

    resp = client.get(f"/api/automations/{other_auto.id}/")
    assert resp.status_code == status.HTTP_404_NOT_FOUND

    list_resp = client.get("/api/automations/")
    ids = [a["id"] for a in list_resp.json()["results"]]
    assert other_auto.id not in ids
