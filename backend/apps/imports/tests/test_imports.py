"""CSV import tests. Maps to TC-58 (5k-row CSV import)."""

from __future__ import annotations

import io

import pytest
from allauth.account.models import EmailAddress
from rest_framework import status
from rest_framework.test import APIClient

from apps.contacts.models import Contact
from apps.imports.mappings import normalize, suggest_mapping
from apps.imports.models import ImportRun, ImportStatus
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
    return client, workspace, user


# --- Heuristic mapper unit tests ---


def test_normalize_handles_messy_headers() -> None:
    assert normalize("First Name") == "first_name"
    assert normalize("E-mail Address") == "e_mail_address"
    assert normalize("  TITLE  ") == "title"


def test_suggest_mapping_for_contact_headers() -> None:
    headers = ["First Name", "Last Name", "Email", "Job Title", "Random"]
    mapping = suggest_mapping(headers, "contact")
    assert mapping == {
        "0": "first_name",
        "1": "last_name",
        "2": "primary_email",
        "3": "title",
    }


def test_suggest_mapping_for_company_headers() -> None:
    headers = ["Company Name", "Domain", "Industry"]
    mapping = suggest_mapping(headers, "company")
    assert mapping["0"] == "name"
    assert mapping["1"] == "domain"
    assert mapping["2"] == "industry"


# --- Upload + commit flow ---


@pytest.mark.django_db
def test_upload_returns_suggested_mapping(admin_session):  # type: ignore[no-untyped-def]
    client, workspace, _ = admin_session
    csv_body = "First Name,Last Name,Email\nAda,Lovelace,ada@example.com\nGrace,Hopper,grace@example.com\n"
    upload = io.BytesIO(csv_body.encode("utf-8"))
    upload.name = "contacts.csv"

    resp = client.post(
        "/api/imports/upload/",
        {"entity_type": "contact", "file": upload},
        format="multipart",
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.content
    body = resp.json()
    assert body["entity_type"] == "contact"
    assert body["mapping"] == {"0": "first_name", "1": "last_name", "2": "primary_email"}
    assert body["total_rows"] == 2
    assert body["headers"] == ["First Name", "Last Name", "Email"]
    assert len(body["sample_rows"]) == 2


@pytest.mark.django_db
def test_commit_runs_import_and_creates_contacts(admin_session):  # type: ignore[no-untyped-def]
    """TC-58 small slice: upload + commit + import succeeds end-to-end with Celery eager."""
    client, workspace, user = admin_session
    csv_body = "First Name,Last Name,Email\nAda,Lovelace,ada@example.com\nGrace,Hopper,grace@example.com\n"
    upload = io.BytesIO(csv_body.encode("utf-8"))
    upload.name = "contacts.csv"

    upload_resp = client.post(
        "/api/imports/upload/",
        {"entity_type": "contact", "file": upload},
        format="multipart",
    )
    run_id = upload_resp.json()["id"]

    commit_resp = client.post(f"/api/imports/{run_id}/commit/")
    assert commit_resp.status_code == status.HTTP_200_OK, commit_resp.content

    run = ImportRun.objects.get(pk=run_id)
    assert run.status == ImportStatus.COMPLETE
    assert run.processed_rows == 2
    assert run.error_rows == 0

    emails = set(Contact.objects.filter(workspace=workspace).values_list("primary_email", flat=True))
    assert emails == {"ada@example.com", "grace@example.com"}


@pytest.mark.django_db
def test_commit_rejects_running_import(admin_session):  # type: ignore[no-untyped-def]
    client, workspace, user = admin_session
    run = ImportRun.objects.create(
        workspace=workspace,
        entity_type="contact",
        status=ImportStatus.RUNNING,
        created_by=user,
    )
    resp = client.post(f"/api/imports/{run.id}/commit/")
    assert resp.status_code == status.HTTP_409_CONFLICT


@pytest.mark.django_db
def test_non_admin_cannot_upload(admin_session):  # type: ignore[no-untyped-def]
    """Imports require admin role."""
    _, workspace, _ = admin_session

    rep = _verified_user("rep@example.com")
    Membership.objects.create(workspace=workspace, user=rep, role=Role.REP)
    rep_client = APIClient()
    access = _login(rep_client, "rep@example.com")
    rep_client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access}",
        HTTP_X_WORKSPACE_ID=str(workspace.id),
    )

    upload = io.BytesIO(b"a,b\n1,2\n")
    upload.name = "x.csv"
    resp = rep_client.post(
        "/api/imports/upload/",
        {"entity_type": "contact", "file": upload},
        format="multipart",
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN
