"""End-to-end contact tests covering M4 acceptance criteria.

Maps to TC-10 (create contact), TC-11 (edit), TC-12 (archive), TC-13 (nav
contact ↔ company), TC-23 (filter by custom field).
"""

from __future__ import annotations

import json

import pytest
from allauth.account.models import EmailAddress
from rest_framework import status
from rest_framework.test import APIClient

from apps.companies.models import Company
from apps.contacts.filters import evaluate_filter_dsl
from apps.contacts.models import Contact
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
def test_create_and_list_contact(owner_session):  # type: ignore[no-untyped-def]
    client, _, _ = owner_session
    resp = client.post(
        "/api/contacts/",
        {
            "first_name": "Ada",
            "last_name": "Lovelace",
            "primary_email": "ada@example.com",
            "title": "Mathematician",
            "lifecycle_stage": "lead",
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.content
    body = resp.json()
    assert body["primary_email"] == "ada@example.com"

    list_resp = client.get("/api/contacts/")
    assert list_resp.status_code == status.HTTP_200_OK
    emails = {c["primary_email"] for c in list_resp.json()["results"]}
    assert "ada@example.com" in emails


@pytest.mark.django_db
def test_edit_contact_inline(owner_session):  # type: ignore[no-untyped-def]
    client, workspace, user = owner_session
    contact = Contact.objects.create(
        workspace=workspace,
        first_name="Ada",
        last_name="Lovelace",
        primary_email="ada@example.com",
        created_by=user,
    )
    resp = client.patch(
        f"/api/contacts/{contact.id}/",
        {"title": "Engineer"},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK, resp.content
    contact.refresh_from_db()
    assert contact.title == "Engineer"


@pytest.mark.django_db
def test_archive_contact(owner_session):  # type: ignore[no-untyped-def]
    client, workspace, user = owner_session
    contact = Contact.objects.create(
        workspace=workspace, first_name="Ada", primary_email="ada@example.com", created_by=user
    )
    resp = client.delete(f"/api/contacts/{contact.id}/")
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    contact.refresh_from_db()
    assert contact.deleted_at is not None
    list_resp = client.get("/api/contacts/")
    emails = {c["primary_email"] for c in list_resp.json()["results"]}
    assert "ada@example.com" not in emails


@pytest.mark.django_db
def test_contact_company_link(owner_session):  # type: ignore[no-untyped-def]
    """TC-13 — contact links to a company; the company's contacts list reflects it."""
    client, workspace, user = owner_session
    company = Company.objects.create(workspace=workspace, name="Stripe", created_by=user)
    resp = client.post(
        "/api/contacts/",
        {"first_name": "Patrick", "last_name": "Collison", "company": company.id},
        format="json",
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.content
    contact_id = resp.json()["id"]

    company.refresh_from_db()
    assert company.contacts.filter(id=contact_id).exists()


@pytest.mark.django_db
def test_filter_dsl_by_custom_field(owner_session):  # type: ignore[no-untyped-def]
    """TC-23 — filter contacts by custom field via the DSL."""
    client, workspace, user = owner_session
    Contact.objects.create(
        workspace=workspace,
        first_name="A",
        custom={"lead_score": 90},
        created_by=user,
    )
    Contact.objects.create(
        workspace=workspace,
        first_name="B",
        custom={"lead_score": 30},
        created_by=user,
    )

    filter_json = json.dumps(
        {"and": [{"field": "custom.lead_score", "op": "gt", "value": 70}]}
    )
    resp = client.get(f"/api/contacts/?filter={filter_json}")
    assert resp.status_code == status.HTTP_200_OK
    names = {c["first_name"] for c in resp.json()["results"]}
    assert names == {"A"}


@pytest.mark.django_db
def test_filter_dsl_rejects_unknown_field(owner_session):  # type: ignore[no-untyped-def]
    client, _, _ = owner_session
    bad_filter = json.dumps({"field": "password", "op": "eq", "value": "x"})
    resp = client.get(f"/api/contacts/?filter={bad_filter}")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_filter_dsl_unit_negation_and_boolean_logic() -> None:
    """Pure unit test for the DSL — no DB needed."""
    allowed = {"name", "email", "custom"}
    q = evaluate_filter_dsl(
        {
            "and": [
                {"field": "name", "op": "eq", "value": "Ada"},
                {"or": [
                    {"field": "email", "op": "icontains", "value": "@stripe.com"},
                    {"field": "custom.lead_score", "op": "gte", "value": 80},
                ]},
                {"not": {"field": "name", "op": "eq", "value": "Bob"}},
            ]
        },
        allowed,
    )
    # Q is opaque; just assert it constructs without raising.
    assert q is not None
