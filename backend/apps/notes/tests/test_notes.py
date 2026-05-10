"""Note tests. Maps to TC-21."""

from __future__ import annotations

from datetime import timedelta

import pytest
from allauth.account.models import EmailAddress
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.contacts.models import Contact
from apps.notes.models import Note
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
def session(db):  # type: ignore[no-untyped-def]
    user = _verified_user("rep@example.com")
    workspace = Workspace.objects.create(name="Acme", slug="acme", created_by=user)
    Membership.objects.create(workspace=workspace, user=user, role=Role.OWNER)
    client = APIClient()
    access = _login(client, "rep@example.com")
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access}",
        HTTP_X_WORKSPACE_ID=str(workspace.id),
    )
    return client, workspace, user


@pytest.mark.django_db
def test_add_markdown_note_to_contact(session):  # type: ignore[no-untyped-def]
    """TC-21 — rep adds a Markdown note to a contact."""
    client, workspace, user = session
    contact = Contact.objects.create(
        workspace=workspace, first_name="Ada", primary_email="ada@example.com", created_by=user
    )

    resp = client.post(
        "/api/notes/",
        {
            "body_md": "**Key**: discount-blocked by procurement. Follow up Friday.",
            "related_type": "contact",
            "related_id": contact.id,
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.content
    body = resp.json()
    assert body["body_md"].startswith("**Key**")
    assert body["author"] == user.id


@pytest.mark.django_db
def test_edit_within_24h_is_silent(session):  # type: ignore[no-untyped-def]
    client, workspace, user = session
    note = Note.objects.create(
        workspace=workspace,
        body_md="original",
        related_type="contact",
        related_id=1,
        author=user,
    )

    resp = client.patch(f"/api/notes/{note.id}/", {"body_md": "edited"}, format="json")
    assert resp.status_code == status.HTTP_200_OK
    note.refresh_from_db()
    assert note.body_md == "edited"
    assert note.edit_log == []


@pytest.mark.django_db
def test_edit_past_24h_creates_audit_row(session):  # type: ignore[no-untyped-def]
    client, workspace, user = session
    note = Note.objects.create(
        workspace=workspace,
        body_md="original",
        related_type="contact",
        related_id=1,
        author=user,
    )
    # Backdate the note past the 24h window.
    Note.objects.filter(pk=note.pk).update(created_at=timezone.now() - timedelta(hours=25))

    resp = client.patch(f"/api/notes/{note.id}/", {"body_md": "edited late"}, format="json")
    assert resp.status_code == status.HTTP_200_OK
    note.refresh_from_db()
    assert note.body_md == "edited late"
    assert len(note.edit_log) == 1
    entry = note.edit_log[0]
    assert entry["edited_by"] == user.id
    assert entry["previous_body_preview"].startswith("original")


@pytest.mark.django_db
def test_filter_notes_by_record(session):  # type: ignore[no-untyped-def]
    client, workspace, user = session
    Note.objects.create(
        workspace=workspace, body_md="A", related_type="contact", related_id=1, author=user
    )
    Note.objects.create(
        workspace=workspace, body_md="B", related_type="contact", related_id=2, author=user
    )

    resp = client.get("/api/notes/?related_type=contact&related_id=1")
    bodies = {n["body_md"] for n in resp.json()["results"]}
    assert bodies == {"A"}
