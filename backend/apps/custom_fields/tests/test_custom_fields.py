"""Tests for custom field definitions. Maps to TC-22, TC-24."""

from __future__ import annotations

import pytest
from allauth.account.models import EmailAddress
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User
from apps.workspaces.models import Membership, Role, Workspace


def _verified_user(email: str) -> User:
    user = User.objects.create_user(email=email, password="VerySecurePass123!")
    EmailAddress.objects.create(user=user, email=email, verified=True, primary=True)
    return user


def _login(client: APIClient, email: str) -> str:
    resp = client.post(
        "/api/auth/login/", {"email": email, "password": "VerySecurePass123!"}, format="json"
    )
    return resp.json()["access"]


@pytest.fixture
def admin_session(db):  # type: ignore[no-untyped-def]
    user = _verified_user("admin@example.com")
    workspace = Workspace.objects.create(name="Acme", slug="acme", created_by=user)
    Membership.objects.create(workspace=workspace, user=user, role=Role.OWNER)
    client = APIClient()
    access = _login(client, "admin@example.com")
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access}",
        HTTP_X_WORKSPACE_ID=str(workspace.id),
    )
    return client, workspace


@pytest.mark.django_db
def test_admin_creates_lead_score_custom_field(admin_session):  # type: ignore[no-untyped-def]
    """TC-22 — admin defines a `number` custom field on contacts."""
    client, _ = admin_session
    resp = client.post(
        "/api/custom-field-defs/",
        {
            "entity_type": "contact",
            "key": "lead_score",
            "label": "Lead Score",
            "type": "number",
            "required": False,
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.content
    body = resp.json()
    assert body["key"] == "lead_score"
    assert body["type"] == "number"


@pytest.mark.django_db
def test_admin_creates_select_with_options(admin_session):  # type: ignore[no-untyped-def]
    """TC-24 — `select` field with options."""
    client, _ = admin_session
    resp = client.post(
        "/api/custom-field-defs/",
        {
            "entity_type": "contact",
            "key": "tier",
            "label": "Tier",
            "type": "select",
            "options": ["A", "B", "C"],
            "required": True,
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.content
    body = resp.json()
    assert body["options"] == ["A", "B", "C"]
    assert body["required"] is True


@pytest.mark.django_db
def test_duplicate_key_per_entity_is_rejected(admin_session):  # type: ignore[no-untyped-def]
    client, _ = admin_session
    payload = {
        "entity_type": "contact",
        "key": "score",
        "label": "Score",
        "type": "number",
    }
    first = client.post("/api/custom-field-defs/", payload, format="json")
    assert first.status_code == status.HTTP_201_CREATED
    second = client.post("/api/custom-field-defs/", payload, format="json")
    assert second.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_filter_by_entity_type(admin_session):  # type: ignore[no-untyped-def]
    client, _ = admin_session
    client.post(
        "/api/custom-field-defs/",
        {"entity_type": "contact", "key": "score", "label": "Score", "type": "number"},
        format="json",
    )
    client.post(
        "/api/custom-field-defs/",
        {"entity_type": "company", "key": "arr", "label": "ARR", "type": "number"},
        format="json",
    )

    resp = client.get("/api/custom-field-defs/?entity_type=contact")
    keys = {f["key"] for f in resp.json()["results"]}
    assert keys == {"score"}
