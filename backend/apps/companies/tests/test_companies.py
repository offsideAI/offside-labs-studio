"""End-to-end company tests covering M4 acceptance criteria.

Maps to TC-4 (companies CRUD), TC-13 (cross-record nav — partial; full nav
lands when contacts→companies link is exercised in test_contacts.py).
"""

from __future__ import annotations

import pytest
from allauth.account.models import EmailAddress
from rest_framework import status
from rest_framework.test import APIClient

from apps.companies.models import Company
from apps.users.models import User
from apps.workspaces.models import Membership, Role, Workspace


def _verified_user(email: str, password: str = "VerySecurePass123!") -> User:
    user = User.objects.create_user(email=email, password=password)
    EmailAddress.objects.create(user=user, email=email, verified=True, primary=True)
    return user


def _login(client: APIClient, email: str) -> str:
    resp = client.post(
        "/api/auth/login/", {"email": email, "password": "VerySecurePass123!"}, format="json"
    )
    return resp.json()["access"]


@pytest.fixture
def workspace_owner_client(db):  # type: ignore[no-untyped-def]
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
def test_owner_creates_and_lists_company(workspace_owner_client):  # type: ignore[no-untyped-def]
    client, workspace, _ = workspace_owner_client

    create_resp = client.post(
        "/api/companies/",
        {"name": "Stripe", "domain": "stripe.com", "industry": "Payments", "size_band": "1000+"},
        format="json",
    )
    assert create_resp.status_code == status.HTTP_201_CREATED, create_resp.content
    body = create_resp.json()
    assert body["name"] == "Stripe"
    assert body["domain"] == "stripe.com"

    list_resp = client.get("/api/companies/")
    assert list_resp.status_code == status.HTTP_200_OK
    names = {c["name"] for c in list_resp.json()["results"]}
    assert "Stripe" in names


@pytest.mark.django_db
def test_company_isolated_to_workspace(workspace_owner_client):  # type: ignore[no-untyped-def]
    """Companies created in workspace A are invisible from workspace B."""
    client, ws_a, _ = workspace_owner_client
    Company.objects.create(workspace=ws_a, name="Stripe", created_by_id=ws_a.created_by_id)

    other_user = _verified_user("intruder@example.com")
    ws_b = Workspace.objects.create(name="Other", slug="other", created_by=other_user)
    Membership.objects.create(workspace=ws_b, user=other_user, role=Role.OWNER)

    other_client = APIClient()
    access = _login(other_client, "intruder@example.com")
    other_client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access}",
        HTTP_X_WORKSPACE_ID=str(ws_b.id),
    )
    resp = other_client.get("/api/companies/")
    assert resp.json()["results"] == []


@pytest.mark.django_db
def test_company_soft_delete(workspace_owner_client):  # type: ignore[no-untyped-def]
    client, workspace, _ = workspace_owner_client
    company = Company.objects.create(
        workspace=workspace, name="DeleteMe", created_by_id=workspace.created_by_id
    )

    resp = client.delete(f"/api/companies/{company.id}/")
    assert resp.status_code == status.HTTP_204_NO_CONTENT

    company.refresh_from_db()
    assert company.deleted_at is not None

    list_resp = client.get("/api/companies/")
    names = {c["name"] for c in list_resp.json()["results"]}
    assert "DeleteMe" not in names
