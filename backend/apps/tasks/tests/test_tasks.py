"""Task tests. Maps to TC-19, TC-20."""

from __future__ import annotations

import pytest
from allauth.account.models import EmailAddress
from rest_framework import status
from rest_framework.test import APIClient

from apps.contacts.models import Contact
from apps.tasks.models import Task, TaskStatus
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
def test_create_task_on_contact(session):  # type: ignore[no-untyped-def]
    """TC-19 — rep adds a task on a contact."""
    client, workspace, user = session
    contact = Contact.objects.create(
        workspace=workspace, first_name="Ada", primary_email="ada@example.com", created_by=user
    )

    resp = client.post(
        "/api/tasks/",
        {
            "title": "Send pricing",
            "due_at": "2026-05-20T17:00:00Z",
            "related_type": "contact",
            "related_id": contact.id,
            "owner": user.id,
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.content
    body = resp.json()
    assert body["title"] == "Send pricing"
    assert body["status"] == "open"


@pytest.mark.django_db
def test_completing_task_stamps_completed_at(session):  # type: ignore[no-untyped-def]
    client, workspace, user = session
    task = Task.objects.create(
        workspace=workspace,
        title="Test",
        related_type="contact",
        related_id=1,
        created_by=user,
    )

    resp = client.patch(f"/api/tasks/{task.id}/", {"status": "done"}, format="json")
    assert resp.status_code == status.HTTP_200_OK
    task.refresh_from_db()
    assert task.status == TaskStatus.DONE
    assert task.completed_at is not None


@pytest.mark.django_db
def test_reopening_task_clears_completed_at(session):  # type: ignore[no-untyped-def]
    client, workspace, user = session
    from django.utils import timezone

    task = Task.objects.create(
        workspace=workspace,
        title="Test",
        related_type="contact",
        related_id=1,
        status=TaskStatus.DONE,
        completed_at=timezone.now(),
        created_by=user,
    )

    resp = client.patch(f"/api/tasks/{task.id}/", {"status": "open"}, format="json")
    assert resp.status_code == status.HTTP_200_OK
    task.refresh_from_db()
    assert task.status == TaskStatus.OPEN
    assert task.completed_at is None


@pytest.mark.django_db
def test_filter_tasks_by_related(session):  # type: ignore[no-untyped-def]
    client, workspace, user = session
    Task.objects.create(
        workspace=workspace, title="A", related_type="contact", related_id=1, created_by=user
    )
    Task.objects.create(
        workspace=workspace, title="B", related_type="contact", related_id=2, created_by=user
    )

    resp = client.get("/api/tasks/?related_type=contact&related_id=1")
    assert resp.status_code == status.HTTP_200_OK
    titles = {t["title"] for t in resp.json()["results"]}
    assert titles == {"A"}


@pytest.mark.django_db
def test_task_invalid_related_type_rejected(session):  # type: ignore[no-untyped-def]
    """Tasks can only attach to contact / company / deal — not to other tasks or notes."""
    client, _, user = session
    resp = client.post(
        "/api/tasks/",
        {
            "title": "Bad",
            "related_type": "task",
            "related_id": 1,
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
