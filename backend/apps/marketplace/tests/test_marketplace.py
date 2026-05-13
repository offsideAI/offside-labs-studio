"""Agents Marketplace tests (M9.S4 / FR-26) — TC-92..TC-94.

- TC-92: catalog list + detail readable anonymously (no auth).
- TC-93: install round-trip creates Automation + AutomationVersion +
         WorkspaceAgentInstall + bumps install_count atomically.
- TC-94: edits made to the installed Automation don't propagate back
         to the catalog (verifies the snapshot semantics).

Plus: hides unpublished agents from anonymous browse; manager-gated
install; __INSTALLER__ sentinel resolves at install time.
"""

from __future__ import annotations

import pytest
from allauth.account.models import EmailAddress
from rest_framework import status
from rest_framework.test import APIClient

from apps.automations.models import (
    Automation,
    AutomationStatus,
    AutomationVersion,
)
from apps.marketplace.models import (
    MarketplaceAgent,
    MarketplaceAgentCategory,
    WorkspaceAgentInstall,
)
from apps.users.models import User
from apps.workspaces.models import Membership, Role, Workspace


SIMPLE_AGENT_GRAPH = {
    "start_node_id": "n1",
    "nodes": {
        "n1": {
            "type": "action",
            "config": {"action": "noop", "input": {"hello": "world"}},
            "next": "end",
        },
        "end": {"type": "end"},
    },
}

AGENT_WITH_SENTINEL_GRAPH = {
    "start_node_id": "n1",
    "nodes": {
        "n1": {
            "type": "action",
            "config": {
                "action": "crm.create_note",
                "input": {
                    "body_md": "auto-note",
                    "related_type": "contact",
                    "related_id": 1,
                    "author_id": "__INSTALLER__",
                },
            },
            "next": "end",
        },
        "end": {"type": "end"},
    },
}


def _verified_user(email: str) -> User:
    user = User.objects.create_user(email=email, password="VerySecurePass123!")
    EmailAddress.objects.create(user=user, email=email, verified=True, primary=True)
    return user


def _login(client: APIClient, email: str) -> str:
    resp = client.post(
        "/api/auth/login/",
        {"email": email, "password": "VerySecurePass123!"},
        format="json",
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


@pytest.fixture
def seeded_agent(db):  # type: ignore[no-untyped-def]
    return MarketplaceAgent.objects.create(
        slug="lead-qualification",
        name="Lead qualification",
        description="Auto-creates a follow-up task on new contacts.",
        category=MarketplaceAgentCategory.LEAD_MANAGEMENT,
        icon_emoji="🎯",
        graph=SIMPLE_AGENT_GRAPH,
        trigger={"type": "record", "entity_type": "contact", "event": "created"},
    )


# --- TC-92: catalog readable anonymously --------------------------------------


@pytest.mark.django_db
def test_catalog_list_anon(seeded_agent) -> None:  # type: ignore[no-untyped-def]
    """TC-92 — catalog list endpoint requires no auth."""
    client = APIClient()  # no credentials, no workspace header
    resp = client.get("/api/marketplace/agents/")
    assert resp.status_code == 200, resp.content
    body = resp.json()
    results = body.get("results", body)
    slugs = [a["slug"] for a in results]
    assert seeded_agent.slug in slugs
    # List serializer omits the full graph to keep the response small.
    first = next(a for a in results if a["slug"] == seeded_agent.slug)
    assert "graph" not in first


@pytest.mark.django_db
def test_catalog_detail_anon_returns_graph(seeded_agent) -> None:  # type: ignore[no-untyped-def]
    client = APIClient()
    resp = client.get(f"/api/marketplace/agents/{seeded_agent.slug}/")
    assert resp.status_code == 200, resp.content
    body = resp.json()
    assert body["slug"] == seeded_agent.slug
    assert body["graph"] == SIMPLE_AGENT_GRAPH
    assert body["trigger"]["type"] == "record"


@pytest.mark.django_db
def test_catalog_filter_by_category(seeded_agent, db) -> None:  # type: ignore[no-untyped-def]
    MarketplaceAgent.objects.create(
        slug="welcome",
        name="Welcome",
        description="…",
        category=MarketplaceAgentCategory.COMMS,
        graph=SIMPLE_AGENT_GRAPH,
    )
    client = APIClient()
    resp = client.get("/api/marketplace/agents/?category=lead_management")
    assert resp.status_code == 200
    body = resp.json()
    results = body.get("results", body)
    slugs = {a["slug"] for a in results}
    assert "lead-qualification" in slugs
    assert "welcome" not in slugs


@pytest.mark.django_db
def test_unpublished_agents_hidden(db) -> None:  # type: ignore[no-untyped-def]
    MarketplaceAgent.objects.create(
        slug="hidden",
        name="Hidden",
        description="…",
        graph=SIMPLE_AGENT_GRAPH,
        is_published=False,
    )
    client = APIClient()
    resp = client.get("/api/marketplace/agents/")
    body = resp.json()
    results = body.get("results", body)
    slugs = [a["slug"] for a in results]
    assert "hidden" not in slugs

    detail = client.get("/api/marketplace/agents/hidden/")
    assert detail.status_code == 404


# --- TC-93: install round-trip -----------------------------------------------


@pytest.mark.django_db
def test_install_creates_automation_and_audit_row(owner_session, seeded_agent) -> None:  # type: ignore[no-untyped-def]
    """TC-93 — install snapshots the agent into a new published Automation."""
    client, workspace, user = owner_session
    before_count = seeded_agent.install_count

    resp = client.post(f"/api/marketplace/agents/{seeded_agent.slug}/install/", format="json")
    assert resp.status_code == status.HTTP_201_CREATED, resp.content
    body = resp.json()
    assert body["version_number"] == 1
    assert "automation_id" in body

    automation = Automation.objects.get(pk=body["automation_id"])
    assert automation.workspace_id == workspace.id
    assert automation.created_by_id == user.id
    assert automation.name == seeded_agent.name
    assert automation.status == AutomationStatus.ACTIVE
    assert automation.published_version_id is not None
    assert automation.graph == SIMPLE_AGENT_GRAPH
    assert automation.trigger == seeded_agent.trigger

    version = AutomationVersion.objects.get(pk=automation.published_version_id)
    assert version.version_number == 1
    assert version.graph == SIMPLE_AGENT_GRAPH

    install = WorkspaceAgentInstall.objects.get(pk=body["install_id"])
    assert install.workspace_id == workspace.id
    assert install.marketplace_agent_id == seeded_agent.id
    assert install.automation_id == automation.id
    assert install.installed_by_id == user.id

    seeded_agent.refresh_from_db()
    assert seeded_agent.install_count == before_count + 1


@pytest.mark.django_db
def test_install_requires_workspace_header(seeded_agent, db) -> None:  # type: ignore[no-untyped-def]
    """Authed user without X-Workspace-Id can't install."""
    user = _verified_user("nows@example.com")
    Workspace.objects.create(name="Solo", slug="solo", created_by=user)
    client = APIClient()
    access = _login(client, "nows@example.com")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")  # NB: no X-Workspace-Id

    resp = client.post(f"/api/marketplace/agents/{seeded_agent.slug}/install/", format="json")
    # WorkspaceJWTAuthentication rejects requests without a resolvable workspace.
    assert resp.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)


@pytest.mark.django_db
def test_install_requires_manager_role(seeded_agent, db) -> None:  # type: ignore[no-untyped-def]
    """A read-only member can't install (manager-only)."""
    owner = _verified_user("owner2@example.com")
    workspace = Workspace.objects.create(name="W2", slug="w2", created_by=owner)
    Membership.objects.create(workspace=workspace, user=owner, role=Role.OWNER)

    viewer = _verified_user("viewer@example.com")
    Membership.objects.create(workspace=workspace, user=viewer, role=Role.READ_ONLY)

    client = APIClient()
    access = _login(client, "viewer@example.com")
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access}",
        HTTP_X_WORKSPACE_ID=str(workspace.id),
    )

    resp = client.post(f"/api/marketplace/agents/{seeded_agent.slug}/install/", format="json")
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_install_resolves_installer_sentinel(owner_session, db) -> None:  # type: ignore[no-untyped-def]
    """`__INSTALLER__` strings in the agent's graph get replaced with the
    installing user's id at install time, so author_id / created_by_id
    point at a real user in the workspace.
    """
    client, _workspace, user = owner_session
    agent = MarketplaceAgent.objects.create(
        slug="welcome",
        name="Welcome",
        description="…",
        graph=AGENT_WITH_SENTINEL_GRAPH,
        category=MarketplaceAgentCategory.COMMS,
    )
    resp = client.post(f"/api/marketplace/agents/{agent.slug}/install/", format="json")
    assert resp.status_code == 201, resp.content
    automation = Automation.objects.get(pk=resp.json()["automation_id"])
    n1 = automation.graph["nodes"]["n1"]
    assert n1["config"]["input"]["author_id"] == user.id  # sentinel resolved


# --- TC-94: edit-after-install doesn't bleed back to catalog ------------------


@pytest.mark.django_db
def test_edit_after_install_does_not_mutate_catalog(owner_session, seeded_agent) -> None:  # type: ignore[no-untyped-def]
    """TC-94 — installed workflow edits are isolated from the catalog row."""
    client, _ws, _user = owner_session
    resp = client.post(f"/api/marketplace/agents/{seeded_agent.slug}/install/", format="json")
    automation_id = resp.json()["automation_id"]

    edited_graph = {
        "start_node_id": "n1",
        "nodes": {
            "n1": {
                "type": "action",
                "config": {"action": "log", "input": {"customized": True}},
                "next": "end",
            },
            "end": {"type": "end"},
        },
    }
    patch = client.patch(
        f"/api/automations/{automation_id}/",
        {"graph": edited_graph},
        format="json",
    )
    assert patch.status_code == 200, patch.content

    # Workspace's automation now has the edited graph.
    automation = Automation.objects.get(pk=automation_id)
    assert automation.graph == edited_graph

    # Catalog row is untouched.
    seeded_agent.refresh_from_db()
    assert seeded_agent.graph == SIMPLE_AGENT_GRAPH

    # The published v1 snapshot on the workspace is also untouched
    # (immutable per M8.S2).
    v1 = AutomationVersion.objects.get(pk=automation.published_version_id)
    assert v1.graph == SIMPLE_AGENT_GRAPH


@pytest.mark.django_db
def test_re_install_creates_separate_automation_rows(owner_session, seeded_agent) -> None:  # type: ignore[no-untyped-def]
    """Installing the same agent twice creates two independent automations."""
    client, workspace, _user = owner_session
    r1 = client.post(f"/api/marketplace/agents/{seeded_agent.slug}/install/", format="json")
    r2 = client.post(f"/api/marketplace/agents/{seeded_agent.slug}/install/", format="json")
    assert r1.json()["automation_id"] != r2.json()["automation_id"]
    assert WorkspaceAgentInstall.objects.filter(workspace=workspace).count() == 2
    seeded_agent.refresh_from_db()
    assert seeded_agent.install_count == 2
