"""Deal + Pipeline tests. Maps to TC-15..TC-18."""

from __future__ import annotations

import pytest
from allauth.account.models import EmailAddress
from rest_framework import status
from rest_framework.test import APIClient

from apps.companies.models import Company
from apps.contacts.models import Contact
from apps.deals.models import Deal, Pipeline, default_pipeline_stages
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
def test_create_pipeline_with_default_stages(owner_session):  # type: ignore[no-untyped-def]
    """TC-15 — manager creates a pipeline with custom stages."""
    client, _, _ = owner_session

    resp = client.post(
        "/api/pipelines/",
        {
            "name": "Outbound Q3",
            "stages": [
                {"id": "prospect", "label": "Prospect", "order": 1},
                {"id": "discovery", "label": "Discovery", "order": 2},
                {"id": "demo", "label": "Demo", "order": 3},
                {"id": "negotiation", "label": "Negotiation", "order": 4},
                {"id": "won", "label": "Closed Won", "order": 5},
                {"id": "lost", "label": "Closed Lost", "order": 6},
            ],
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.content
    body = resp.json()
    assert body["name"] == "Outbound Q3"
    assert len(body["stages"]) == 6


@pytest.mark.django_db
def test_default_pipeline_stages_helper() -> None:
    stages = default_pipeline_stages()
    ids = [s["id"] for s in stages]
    assert ids == ["lead", "qualified", "demo", "negotiation", "closed_won", "closed_lost"]


@pytest.mark.django_db
def test_create_deal_with_contact_and_company(owner_session):  # type: ignore[no-untyped-def]
    """TC-16 — rep creates a deal with contact + company."""
    client, workspace, user = owner_session
    pipeline = Pipeline.objects.create(workspace=workspace, name="P", created_by=user)
    company = Company.objects.create(workspace=workspace, name="Acme Co", created_by=user)
    contact = Contact.objects.create(
        workspace=workspace, first_name="Ada", primary_email="ada@example.com", created_by=user
    )

    resp = client.post(
        "/api/deals/",
        {
            "name": "Acme Q3 expansion",
            "pipeline": pipeline.id,
            "stage_id": "discovery",
            "value_cents": 2_400_000,
            "currency": "USD",
            "company": company.id,
            "contact": contact.id,
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.content
    body = resp.json()
    assert body["name"] == "Acme Q3 expansion"
    assert body["stage_id"] == "discovery"
    assert body["value_cents"] == 2_400_000


@pytest.mark.django_db
def test_move_deal_across_stages(owner_session):  # type: ignore[no-untyped-def]
    """TC-17 — drag deal across stages updates stage_id."""
    client, workspace, user = owner_session
    pipeline = Pipeline.objects.create(workspace=workspace, name="P", created_by=user)
    deal = Deal.objects.create(
        workspace=workspace,
        name="Test deal",
        pipeline=pipeline,
        stage_id="discovery",
        created_by=user,
    )

    resp = client.patch(
        f"/api/deals/{deal.id}/", {"stage_id": "demo"}, format="json"
    )
    assert resp.status_code == status.HTTP_200_OK, resp.content
    deal.refresh_from_db()
    assert deal.stage_id == "demo"


@pytest.mark.django_db
def test_close_deal(owner_session):  # type: ignore[no-untyped-def]
    """TC-18 — rep closes a deal by moving to closed_won stage."""
    client, workspace, user = owner_session
    pipeline = Pipeline.objects.create(workspace=workspace, name="P", created_by=user)
    deal = Deal.objects.create(
        workspace=workspace,
        name="Closing deal",
        pipeline=pipeline,
        stage_id="negotiation",
        value_cents=10_000_00,
        created_by=user,
    )

    resp = client.patch(f"/api/deals/{deal.id}/", {"stage_id": "closed_won"}, format="json")
    assert resp.status_code == status.HTTP_200_OK
    deal.refresh_from_db()
    assert deal.stage_id == "closed_won"


@pytest.mark.django_db
def test_deal_isolated_to_workspace(owner_session):  # type: ignore[no-untyped-def]
    client, ws_a, user_a = owner_session
    pipeline_a = Pipeline.objects.create(workspace=ws_a, name="P", created_by=user_a)
    Deal.objects.create(
        workspace=ws_a, name="A's deal", pipeline=pipeline_a, stage_id="lead", created_by=user_a
    )

    other = _verified_user("other@example.com")
    ws_b = Workspace.objects.create(name="Other", slug="other", created_by=other)
    Membership.objects.create(workspace=ws_b, user=other, role=Role.OWNER)

    other_client = APIClient()
    access = _login(other_client, "other@example.com")
    other_client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access}",
        HTTP_X_WORKSPACE_ID=str(ws_b.id),
    )

    resp = other_client.get("/api/deals/")
    assert resp.json()["results"] == []
