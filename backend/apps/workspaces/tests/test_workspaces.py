"""End-to-end workspace tests covering M2 acceptance criteria.

Maps to TC-5 (invite a teammate), TC-6 (promote to manager), TC-7 (switch
workspaces), TC-8 (cross-workspace data is invisible), TC-9 (archive workspace
deferred — soft-delete is in place).
"""

from __future__ import annotations

import pytest
from allauth.account.models import EmailAddress
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User
from apps.workspaces.models import Invitation, Membership, Role, Workspace


def _verified_user(email: str, password: str = "VerySecurePass123!", full_name: str = "") -> User:
    user = User.objects.create_user(email=email, password=password, full_name=full_name)
    EmailAddress.objects.create(user=user, email=email, verified=True, primary=True)
    return user


def _login(client: APIClient, email: str, password: str = "VerySecurePass123!") -> str:
    resp = client.post(
        "/api/auth/login/",
        {"email": email, "password": password},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK, resp.content
    return resp.json()["access"]


@pytest.mark.django_db
def test_owner_creates_workspace_and_is_owner_member() -> None:
    user = _verified_user("alice@example.com")
    client = APIClient()
    access = _login(client, "alice@example.com")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    resp = client.post("/api/workspaces/", {"name": "Acme Sales"}, format="json")
    assert resp.status_code == status.HTTP_201_CREATED, resp.content
    body = resp.json()
    assert body["name"] == "Acme Sales"
    assert body["slug"] == "acme-sales"
    assert body["role"] == Role.OWNER

    # Membership exists.
    membership = Membership.objects.get(workspace_id=body["id"], user=user)
    assert membership.role == Role.OWNER


@pytest.mark.django_db
def test_owner_invites_teammate_and_teammate_accepts() -> None:
    owner = _verified_user("owner@example.com")
    workspace = Workspace.objects.create(
        name="Acme Sales",
        slug="acme-sales",
        created_by=owner,
    )
    Membership.objects.create(workspace=workspace, user=owner, role=Role.OWNER)

    client = APIClient()
    access = _login(client, "owner@example.com")
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access}",
        HTTP_X_WORKSPACE_ID=str(workspace.id),
    )

    # Invite.
    invite_resp = client.post(
        "/api/invitations/",
        {"email": "rep@example.com", "role": Role.REP},
        format="json",
    )
    assert invite_resp.status_code == status.HTTP_201_CREATED, invite_resp.content
    invitation = Invitation.objects.get(email="rep@example.com")

    # Public detail (unauthenticated).
    public_client = APIClient()
    detail_resp = public_client.get(f"/api/invitations/{invitation.token}/")
    assert detail_resp.status_code == status.HTTP_200_OK
    assert detail_resp.json()["workspace_name"] == "Acme Sales"

    # Recipient signs up + verifies, then accepts.
    rep = _verified_user("rep@example.com")
    rep_client = APIClient()
    rep_access = _login(rep_client, "rep@example.com")
    rep_client.credentials(HTTP_AUTHORIZATION=f"Bearer {rep_access}")

    accept_resp = rep_client.post(f"/api/invitations/{invitation.token}/accept/")
    assert accept_resp.status_code == status.HTTP_200_OK, accept_resp.content
    assert accept_resp.json()["role"] == Role.REP

    membership = Membership.objects.get(workspace=workspace, user=rep)
    assert membership.role == Role.REP

    invitation.refresh_from_db()
    assert invitation.is_accepted


@pytest.mark.django_db
def test_invitation_to_wrong_email_is_rejected() -> None:
    owner = _verified_user("owner@example.com")
    workspace = Workspace.objects.create(name="Acme", slug="acme", created_by=owner)
    Membership.objects.create(workspace=workspace, user=owner, role=Role.OWNER)
    invitation = Invitation.objects.create(
        workspace=workspace,
        email="someone@example.com",
        role=Role.REP,
        invited_by=owner,
    )

    intruder = _verified_user("intruder@example.com")
    client = APIClient()
    access = _login(client, "intruder@example.com")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    resp = client.post(f"/api/invitations/{invitation.token}/accept/")
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_cross_workspace_membership_list_returns_empty() -> None:
    """User-A in workspace-A cannot list memberships of workspace-B."""
    user_a = _verified_user("a@example.com")
    user_b = _verified_user("b@example.com")
    ws_a = Workspace.objects.create(name="A", slug="a", created_by=user_a)
    ws_b = Workspace.objects.create(name="B", slug="b", created_by=user_b)
    Membership.objects.create(workspace=ws_a, user=user_a, role=Role.OWNER)
    Membership.objects.create(workspace=ws_b, user=user_b, role=Role.OWNER)

    client = APIClient()
    access = _login(client, "a@example.com")
    # User-A points the X-Workspace-Id header at workspace-B.
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access}",
        HTTP_X_WORKSPACE_ID=str(ws_b.id),
    )

    resp = client.get("/api/memberships/")
    # IsWorkspaceMember rejects because user-A has no membership in ws_b → request.workspace_id=None.
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_workspace_list_only_shows_my_workspaces() -> None:
    user_a = _verified_user("a@example.com")
    user_b = _verified_user("b@example.com")
    ws_a = Workspace.objects.create(name="A", slug="a", created_by=user_a)
    ws_b = Workspace.objects.create(name="B", slug="b", created_by=user_b)
    Membership.objects.create(workspace=ws_a, user=user_a, role=Role.OWNER)
    Membership.objects.create(workspace=ws_b, user=user_b, role=Role.OWNER)

    client = APIClient()
    access = _login(client, "a@example.com")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    resp = client.get("/api/workspaces/")
    assert resp.status_code == status.HTTP_200_OK
    slugs = {w["slug"] for w in resp.json()["results"]}
    assert slugs == {"a"}
    assert "b" not in slugs


@pytest.mark.django_db
def test_invalid_workspace_header_is_ignored() -> None:
    user = _verified_user("alice@example.com")
    workspace = Workspace.objects.create(name="A", slug="a", created_by=user)
    Membership.objects.create(workspace=workspace, user=user, role=Role.OWNER)

    client = APIClient()
    access = _login(client, "alice@example.com")
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access}",
        HTTP_X_WORKSPACE_ID="not-a-number",
    )

    resp = client.get("/api/memberships/")
    # Header doesn't validate → request.workspace_id=None → permission denied.
    assert resp.status_code == status.HTTP_403_FORBIDDEN


# --- M3: settings endpoints (TC-6 role promotion, TC-9 workspace archive) ---


@pytest.mark.django_db
def test_admin_can_promote_a_rep() -> None:
    """TC-6 — admin can change a teammate's role to manager."""
    owner = _verified_user("owner@example.com")
    rep = _verified_user("rep@example.com")
    workspace = Workspace.objects.create(name="A", slug="a", created_by=owner)
    Membership.objects.create(workspace=workspace, user=owner, role=Role.OWNER)
    rep_membership = Membership.objects.create(workspace=workspace, user=rep, role=Role.REP)

    client = APIClient()
    access = _login(client, "owner@example.com")
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access}",
        HTTP_X_WORKSPACE_ID=str(workspace.id),
    )

    resp = client.patch(
        f"/api/memberships/{rep_membership.id}/",
        {"role": Role.MANAGER},
        format="json",
    )
    assert resp.status_code == status.HTTP_200_OK, resp.content
    rep_membership.refresh_from_db()
    assert rep_membership.role == Role.MANAGER


@pytest.mark.django_db
def test_non_admin_cannot_promote() -> None:
    owner = _verified_user("owner@example.com")
    rep_a = _verified_user("rep_a@example.com")
    rep_b = _verified_user("rep_b@example.com")
    workspace = Workspace.objects.create(name="A", slug="a", created_by=owner)
    Membership.objects.create(workspace=workspace, user=owner, role=Role.OWNER)
    Membership.objects.create(workspace=workspace, user=rep_a, role=Role.REP)
    rep_b_m = Membership.objects.create(workspace=workspace, user=rep_b, role=Role.REP)

    client = APIClient()
    access = _login(client, "rep_a@example.com")
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access}",
        HTTP_X_WORKSPACE_ID=str(workspace.id),
    )

    resp = client.patch(
        f"/api/memberships/{rep_b_m.id}/", {"role": Role.MANAGER}, format="json"
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_cannot_demote_owner_via_patch() -> None:
    owner = _verified_user("owner@example.com")
    workspace = Workspace.objects.create(name="A", slug="a", created_by=owner)
    owner_m = Membership.objects.create(workspace=workspace, user=owner, role=Role.OWNER)

    client = APIClient()
    access = _login(client, "owner@example.com")
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access}",
        HTTP_X_WORKSPACE_ID=str(workspace.id),
    )

    resp = client.patch(
        f"/api/memberships/{owner_m.id}/", {"role": Role.ADMIN}, format="json"
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_owner_archives_workspace() -> None:
    """TC-9 — owner soft-deletes the workspace."""
    owner = _verified_user("owner@example.com")
    workspace = Workspace.objects.create(name="A", slug="a", created_by=owner)
    Membership.objects.create(workspace=workspace, user=owner, role=Role.OWNER)

    client = APIClient()
    access = _login(client, "owner@example.com")
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access}",
        HTTP_X_WORKSPACE_ID=str(workspace.id),
    )

    resp = client.post(f"/api/workspaces/{workspace.id}/archive/")
    assert resp.status_code == status.HTTP_200_OK, resp.content

    workspace.refresh_from_db()
    assert workspace.deleted_at is not None

    # Workspace no longer appears in the list.
    list_resp = client.get("/api/workspaces/")
    assert workspace.slug not in {w["slug"] for w in list_resp.json()["results"]}


@pytest.mark.django_db
def test_admin_cannot_archive_workspace() -> None:
    owner = _verified_user("owner@example.com")
    admin = _verified_user("admin@example.com")
    workspace = Workspace.objects.create(name="A", slug="a", created_by=owner)
    Membership.objects.create(workspace=workspace, user=owner, role=Role.OWNER)
    Membership.objects.create(workspace=workspace, user=admin, role=Role.ADMIN)

    client = APIClient()
    access = _login(client, "admin@example.com")
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access}",
        HTTP_X_WORKSPACE_ID=str(workspace.id),
    )

    resp = client.post(f"/api/workspaces/{workspace.id}/archive/")
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    workspace.refresh_from_db()
    assert workspace.deleted_at is None


@pytest.mark.django_db
def test_archive_must_match_active_workspace() -> None:
    """Owner of A and owner of B should not be able to archive A while X-Workspace-Id points at B."""
    user = _verified_user("user@example.com")
    ws_a = Workspace.objects.create(name="A", slug="a", created_by=user)
    ws_b = Workspace.objects.create(name="B", slug="b", created_by=user)
    Membership.objects.create(workspace=ws_a, user=user, role=Role.OWNER)
    Membership.objects.create(workspace=ws_b, user=user, role=Role.OWNER)

    client = APIClient()
    access = _login(client, "user@example.com")
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access}",
        HTTP_X_WORKSPACE_ID=str(ws_b.id),
    )

    resp = client.post(f"/api/workspaces/{ws_a.id}/archive/")
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    ws_a.refresh_from_db()
    assert ws_a.deleted_at is None
