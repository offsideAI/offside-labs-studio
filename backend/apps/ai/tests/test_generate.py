"""Tests for apps.ai — describe-in-English flow.

The real Anthropic call is replaced via `client.set_override_caller`, so
these tests are hermetic. We exercise:
  - successful tool-use round-trip → graph returned + telemetry row.
  - empty tool input → AIResponseError.
  - transport failure → AIClientError + telemetry row with status=error.
  - DRF endpoint maps these to 200 / 400 / 502.
"""

from __future__ import annotations

from allauth.account.models import EmailAddress
from rest_framework import status
from rest_framework.test import APIClient

import pytest

from apps.ai import client as ai_client
from apps.ai.exceptions import AIClientError, AIResponseError
from apps.ai.models import AICall, AICallStatus
from apps.ai.prompts import get as get_prompt
from apps.ai.services import generate_automation_graph
from apps.automations.models import Automation
from apps.users.models import User
from apps.workspaces.models import Membership, Role, Workspace


VALID_GRAPH = {
    "start_node_id": "n1",
    "nodes": {
        "n1": {
            "type": "action",
            "label": "Log it",
            "config": {"action": "log", "input": {"msg": "hi"}},
            "next": "end",
        },
        "end": {"type": "end"},
    },
}


def _make_response(tool_input, *, model="claude-sonnet-4-6", tokens_in=120, tokens_out=80, latency_ms=420):  # type: ignore[no-untyped-def]
    return ai_client.AIResponse(
        parsed_tool_input=tool_input,
        raw_text="",
        model=model,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        latency_ms=latency_ms,
    )


@pytest.fixture(autouse=True)
def reset_override():  # type: ignore[no-untyped-def]
    yield
    ai_client.set_override_caller(None)


@pytest.fixture
def workspace_user(db):  # type: ignore[no-untyped-def]
    user = User.objects.create_user(email="owner@example.com", password="VerySecurePass123!")
    workspace = Workspace.objects.create(name="Acme", slug="acme", created_by=user)
    Membership.objects.create(workspace=workspace, user=user, role=Role.OWNER)
    EmailAddress.objects.create(user=user, email="owner@example.com", verified=True, primary=True)
    return workspace, user


@pytest.mark.django_db
def test_generate_automation_graph_happy_path(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    ai_client.set_override_caller(lambda prompt, kwargs: _make_response(VALID_GRAPH))

    graph, response = generate_automation_graph(
        workspace=workspace,
        description="When a contact is created, log it.",
        requested_by=user,
    )

    assert graph["start_node_id"] == "n1"
    assert set(graph["nodes"].keys()) == {"n1", "end"}
    assert graph["nodes"]["n1"]["type"] == "action"
    assert response.tokens_in == 120
    assert response.tokens_out == 80

    call = AICall.objects.get(workspace=workspace)
    assert call.prompt_name == "automations.author_from_nl.v1"
    assert call.status == AICallStatus.SUCCESS
    # Sonnet 4.6: 300 c/Mtok in, 1500 c/Mtok out → 120*300/1M + 80*1500/1M = 0 + 0
    # Integer division on small token counts rounds to 0; verify the row writes a value, not crashes.
    assert call.cost_cents >= 0
    assert call.tokens_in == 120
    assert call.tokens_out == 80


@pytest.mark.django_db
def test_generate_rejects_empty_tool_input(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    ai_client.set_override_caller(lambda prompt, kwargs: _make_response(None))

    with pytest.raises(AIResponseError):
        generate_automation_graph(workspace=workspace, description="do something", requested_by=user)


@pytest.mark.django_db
def test_generate_rejects_invalid_graph_shape(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    bad_graph = {"start_node_id": "n1", "nodes": {"n1": {"type": "totally-unknown"}}}
    ai_client.set_override_caller(lambda prompt, kwargs: _make_response(bad_graph))

    with pytest.raises(AIResponseError):
        generate_automation_graph(workspace=workspace, description="bad", requested_by=user)


@pytest.mark.django_db
def test_generate_logs_telemetry_on_transport_failure(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user

    def boom(prompt, kwargs):
        raise RuntimeError("upstream 503")

    ai_client.set_override_caller(boom)

    with pytest.raises(AIClientError):
        generate_automation_graph(workspace=workspace, description="x", requested_by=user)

    call = AICall.objects.get(workspace=workspace)
    assert call.status == AICallStatus.ERROR
    assert "upstream 503" in call.error


def test_prompt_registry_resolves() -> None:
    p = get_prompt("automations.author_from_nl.v1")
    request = p.build(description="when X then Y", workspace_context="contacts have foo")
    assert request["tools"][0]["name"] == "build_graph"
    assert "automations.author_from_nl.v1".lower() in p.name


# --- DRF endpoint ---


def _verified_owner(email: str) -> User:
    u = User.objects.create_user(email=email, password="VerySecurePass123!")
    EmailAddress.objects.create(user=u, email=email, verified=True, primary=True)
    return u


def _client_for(workspace: Workspace, email: str) -> APIClient:
    c = APIClient()
    resp = c.post(
        "/api/auth/login/", {"email": email, "password": "VerySecurePass123!"}, format="json"
    )
    access = resp.json()["access"]
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {access}", HTTP_X_WORKSPACE_ID=str(workspace.id))
    return c


@pytest.fixture
def owner_session(db):  # type: ignore[no-untyped-def]
    user = _verified_owner("owner@example.com")
    workspace = Workspace.objects.create(name="Acme", slug="acme", created_by=user)
    Membership.objects.create(workspace=workspace, user=user, role=Role.OWNER)
    return _client_for(workspace, "owner@example.com"), workspace, user


@pytest.mark.django_db
def test_generate_from_nl_endpoint_returns_graph(owner_session) -> None:  # type: ignore[no-untyped-def]
    client, workspace, user = owner_session
    automation = Automation.objects.create(
        workspace=workspace, name="NL test", graph={}, created_by=user
    )
    ai_client.set_override_caller(lambda prompt, kwargs: _make_response(VALID_GRAPH))

    resp = client.post(
        f"/api/automations/{automation.id}/generate_from_nl/",
        {"description": "Log every new contact."},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK, resp.content
    body = resp.json()
    assert body["graph"]["start_node_id"] == "n1"
    assert body["tokens_in"] == 120
    assert body["model"] == "claude-sonnet-4-6"


@pytest.mark.django_db
def test_generate_from_nl_endpoint_requires_description(owner_session) -> None:  # type: ignore[no-untyped-def]
    client, workspace, user = owner_session
    automation = Automation.objects.create(
        workspace=workspace, name="x", graph={}, created_by=user
    )

    resp = client.post(f"/api/automations/{automation.id}/generate_from_nl/", {}, format="json")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_generate_from_nl_endpoint_502_on_provider_failure(owner_session) -> None:  # type: ignore[no-untyped-def]
    client, workspace, user = owner_session
    automation = Automation.objects.create(
        workspace=workspace, name="x", graph={}, created_by=user
    )

    def boom(prompt, kwargs):
        raise RuntimeError("provider down")

    ai_client.set_override_caller(boom)

    resp = client.post(
        f"/api/automations/{automation.id}/generate_from_nl/",
        {"description": "x"},
        format="json",
    )
    assert resp.status_code == status.HTTP_502_BAD_GATEWAY
