"""Activity log tests — signal handlers + filtered list endpoint."""

from __future__ import annotations

import pytest
from allauth.account.models import EmailAddress
from rest_framework import status
from rest_framework.test import APIClient

from apps.activities.models import Activity
from apps.activities.types import ActivityKind, RelatedType
from apps.companies.models import Company
from apps.contacts.models import Contact
from apps.deals.models import Deal, Pipeline
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
def test_creating_contact_records_activity(owner_session):  # type: ignore[no-untyped-def]
    """Signal handler fires on Contact create."""
    _, workspace, user = owner_session
    contact = Contact.objects.create(
        workspace=workspace,
        first_name="Ada",
        primary_email="ada@example.com",
        created_by=user,
    )

    activities = Activity.objects.filter(
        workspace=workspace,
        related_type=RelatedType.CONTACT,
        related_id=contact.id,
    )
    assert activities.count() == 1
    activity = activities.first()
    assert activity is not None
    assert activity.kind == ActivityKind.RECORD_CREATED
    assert activity.actor_user_id == user.id
    assert "primary_email" in activity.payload


@pytest.mark.django_db
def test_creating_company_records_activity(owner_session):  # type: ignore[no-untyped-def]
    _, workspace, user = owner_session
    company = Company.objects.create(workspace=workspace, name="Stripe", created_by=user)
    assert Activity.objects.filter(
        related_type=RelatedType.COMPANY, related_id=company.id, kind=ActivityKind.RECORD_CREATED
    ).exists()


@pytest.mark.django_db
def test_creating_deal_records_activity(owner_session):  # type: ignore[no-untyped-def]
    _, workspace, user = owner_session
    pipeline = Pipeline.objects.create(workspace=workspace, name="P", created_by=user)
    deal = Deal.objects.create(
        workspace=workspace, name="Test", pipeline=pipeline, stage_id="lead", created_by=user
    )
    assert Activity.objects.filter(
        related_type=RelatedType.DEAL, related_id=deal.id, kind=ActivityKind.RECORD_CREATED
    ).exists()


@pytest.mark.django_db
def test_deal_stage_change_records_activity(owner_session):  # type: ignore[no-untyped-def]
    _, workspace, user = owner_session
    pipeline = Pipeline.objects.create(workspace=workspace, name="P", created_by=user)
    deal = Deal.objects.create(
        workspace=workspace, name="Stage", pipeline=pipeline, stage_id="lead", created_by=user
    )
    deal.stage_id = "demo"
    deal.save(update_fields=["stage_id"])
    assert Activity.objects.filter(
        related_type=RelatedType.DEAL,
        related_id=deal.id,
        kind=ActivityKind.DEAL_STAGE_CHANGED,
    ).exists()


@pytest.mark.django_db
def test_activity_filter_by_related(owner_session):  # type: ignore[no-untyped-def]
    """List endpoint filters by related_type + related_id (used by record detail feeds)."""
    client, workspace, user = owner_session
    contact = Contact.objects.create(
        workspace=workspace, first_name="A", primary_email="a@example.com", created_by=user
    )
    Contact.objects.create(
        workspace=workspace, first_name="B", primary_email="b@example.com", created_by=user
    )

    resp = client.get(f"/api/activities/?related_type=contact&related_id={contact.id}")
    assert resp.status_code == status.HTTP_200_OK
    results = resp.json()["results"]
    assert len(results) == 1
    assert results[0]["related_id"] == contact.id


@pytest.mark.django_db
def test_activities_isolated_to_workspace(owner_session):  # type: ignore[no-untyped-def]
    _, ws_a, user_a = owner_session
    Contact.objects.create(
        workspace=ws_a, first_name="A", primary_email="a@example.com", created_by=user_a
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
    resp = other_client.get("/api/activities/")
    assert resp.json()["results"] == []
