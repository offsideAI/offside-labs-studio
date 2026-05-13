"""CRM-mutate action tests (M9.S2 phase 3).

Covers:
- crm.update_contact (happy path, allowed-field filter, not-found, workspace isolation).
- crm.create_company / crm.update_company.
- crm.create_deal (validates stage_id against pipeline; pipeline-not-found).
- crm.update_deal (allowed-field filter, deleted deal not found).
- crm.create_task (validates related_type allowlist).
- crm.create_note.
- All actions registered (so describe-in-English picks them up).
"""

from __future__ import annotations

import pytest

from apps.automations import actions
from apps.automations.exceptions import ActionError
from apps.companies.models import Company
from apps.contacts.models import Contact
from apps.deals.models import Deal, Pipeline, default_pipeline_stages
from apps.notes.models import Note
from apps.tasks.models import Task
from apps.users.models import User
from apps.workspaces.models import Workspace


@pytest.fixture
def workspace_user(db):  # type: ignore[no-untyped-def]
    user = User.objects.create_user(email="owner@example.com", password="VerySecurePass123!")
    workspace = Workspace.objects.create(name="Acme", slug="acme", created_by=user)
    return workspace, user


@pytest.fixture
def pipeline(workspace_user):  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    return Pipeline.objects.create(
        workspace=workspace,
        name="Default",
        stages=default_pipeline_stages(),
        is_default=True,
        created_by=user,
    )


# --- crm.update_contact ---


@pytest.mark.django_db
def test_update_contact_happy_path(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    contact = Contact.objects.create(
        workspace=workspace,
        first_name="Ada",
        last_name="Lovelace",
        primary_email="ada@old.example",
        created_by=user,
    )

    result = actions.action_update_contact(
        workspace,
        {
            "contact_id": contact.id,
            "patch": {"primary_email": "ada@new.example", "title": "Mathematician"},
        },
    )
    contact.refresh_from_db()
    assert contact.primary_email == "ada@new.example"
    assert contact.title == "Mathematician"
    assert set(result["updated_fields"]) == {"primary_email", "title"}


@pytest.mark.django_db
def test_update_contact_rejects_disallowed_field(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    contact = Contact.objects.create(
        workspace=workspace, primary_email="x@example.com", created_by=user
    )
    with pytest.raises(ActionError) as excinfo:
        actions.action_update_contact(
            workspace,
            {"contact_id": contact.id, "patch": {"workspace_id": 999, "first_name": "X"}},
        )
    assert "workspace_id" in str(excinfo.value)


@pytest.mark.django_db
def test_update_contact_not_found_in_workspace(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, _ = workspace_user
    with pytest.raises(ActionError) as excinfo:
        actions.action_update_contact(workspace, {"contact_id": 99999, "patch": {}})
    assert "not found" in str(excinfo.value)


@pytest.mark.django_db
def test_update_contact_respects_workspace_isolation(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, _ = workspace_user
    other_user = User.objects.create_user(email="other@example.com", password="VerySecurePass123!")
    other_ws = Workspace.objects.create(name="Other", slug="other", created_by=other_user)
    other_contact = Contact.objects.create(
        workspace=other_ws, primary_email="hidden@example.com", created_by=other_user
    )

    with pytest.raises(ActionError):
        actions.action_update_contact(
            workspace, {"contact_id": other_contact.id, "patch": {"first_name": "Mallory"}}
        )


@pytest.mark.django_db
def test_update_contact_no_change_returns_empty_updated_fields(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    contact = Contact.objects.create(
        workspace=workspace, first_name="Ada", primary_email="ada@example.com", created_by=user
    )
    result = actions.action_update_contact(
        workspace, {"contact_id": contact.id, "patch": {"first_name": "Ada"}}
    )
    assert result["updated_fields"] == []


# --- crm.create_company + crm.update_company ---


@pytest.mark.django_db
def test_create_and_update_company(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    created = actions.action_create_company(
        workspace,
        {
            "name": "Acme Corp",
            "domain": "acme.example",
            "industry": "Software",
            "created_by_id": user.id,
        },
    )
    assert Company.objects.filter(pk=created["company_id"]).exists()

    updated = actions.action_update_company(
        workspace,
        {"company_id": created["company_id"], "patch": {"industry": "Hardware"}},
    )
    assert updated["updated_fields"] == ["industry"]
    company = Company.objects.get(pk=created["company_id"])
    assert company.industry == "Hardware"


@pytest.mark.django_db
def test_create_company_requires_name(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    with pytest.raises(ActionError):
        actions.action_create_company(workspace, {"created_by_id": user.id})


@pytest.mark.django_db
def test_create_company_requires_created_by(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, _ = workspace_user
    with pytest.raises(ActionError):
        actions.action_create_company(workspace, {"name": "Anon Inc"})


# --- crm.create_deal + crm.update_deal ---


@pytest.mark.django_db
def test_create_deal_happy_path(workspace_user, pipeline) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    result = actions.action_create_deal(
        workspace,
        {
            "name": "Big deal",
            "pipeline_id": pipeline.id,
            "stage_id": "lead",
            "value_cents": 500_000,
            "currency": "USD",
            "created_by_id": user.id,
        },
    )
    deal = Deal.objects.get(pk=result["deal_id"])
    assert deal.stage_id == "lead"
    assert deal.value_cents == 500_000


@pytest.mark.django_db
def test_create_deal_rejects_invalid_stage(workspace_user, pipeline) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    with pytest.raises(ActionError) as excinfo:
        actions.action_create_deal(
            workspace,
            {
                "name": "x",
                "pipeline_id": pipeline.id,
                "stage_id": "not-a-stage",
                "created_by_id": user.id,
            },
        )
    assert "stage_id" in str(excinfo.value)


@pytest.mark.django_db
def test_create_deal_pipeline_not_found(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    with pytest.raises(ActionError):
        actions.action_create_deal(
            workspace,
            {
                "name": "x",
                "pipeline_id": 99999,
                "stage_id": "lead",
                "created_by_id": user.id,
            },
        )


@pytest.mark.django_db
def test_update_deal_allowed_field(workspace_user, pipeline) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    deal = Deal.objects.create(
        workspace=workspace,
        name="Original",
        pipeline=pipeline,
        stage_id="lead",
        value_cents=100,
        created_by=user,
    )
    actions.action_update_deal(
        workspace,
        {"deal_id": deal.id, "patch": {"name": "Renamed", "value_cents": 999}},
    )
    deal.refresh_from_db()
    assert deal.name == "Renamed"
    assert deal.value_cents == 999


@pytest.mark.django_db
def test_update_deal_rejects_disallowed_field(workspace_user, pipeline) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    deal = Deal.objects.create(
        workspace=workspace,
        name="x",
        pipeline=pipeline,
        stage_id="lead",
        created_by=user,
    )
    with pytest.raises(ActionError):
        actions.action_update_deal(
            workspace, {"deal_id": deal.id, "patch": {"created_at": "tampered"}}
        )


# --- crm.create_task ---


@pytest.mark.django_db
def test_create_task_against_contact(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    contact = Contact.objects.create(
        workspace=workspace, primary_email="x@example.com", created_by=user
    )
    result = actions.action_create_task(
        workspace,
        {
            "title": "Follow up",
            "related_type": "contact",
            "related_id": contact.id,
            "priority": "high",
            "created_by_id": user.id,
        },
    )
    task = Task.objects.get(pk=result["task_id"])
    assert task.title == "Follow up"
    assert task.related_type == "contact"
    assert task.priority == "high"


@pytest.mark.django_db
def test_create_task_rejects_bad_related_type(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    with pytest.raises(ActionError):
        actions.action_create_task(
            workspace,
            {
                "title": "x",
                "related_type": "bogus",
                "related_id": 1,
                "created_by_id": user.id,
            },
        )


# --- crm.create_note ---


@pytest.mark.django_db
def test_create_note_against_deal(workspace_user, pipeline) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    deal = Deal.objects.create(
        workspace=workspace, name="x", pipeline=pipeline, stage_id="lead", created_by=user
    )
    result = actions.action_create_note(
        workspace,
        {
            "body_md": "## Followup notes\n- Sent quote",
            "related_type": "deal",
            "related_id": deal.id,
            "author_id": user.id,
        },
    )
    note = Note.objects.get(pk=result["note_id"])
    assert note.related_type == "deal"
    assert note.body_md.startswith("## Followup")


@pytest.mark.django_db
def test_create_note_requires_body(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    with pytest.raises(ActionError):
        actions.action_create_note(
            workspace,
            {"body_md": "", "related_type": "contact", "related_id": 1, "author_id": user.id},
        )


# --- Registry coverage ---


def test_all_crm_actions_registered() -> None:
    names = set(actions.all_names())
    assert {
        "crm.update_contact",
        "crm.create_company",
        "crm.update_company",
        "crm.create_deal",
        "crm.update_deal",
        "crm.create_task",
        "crm.create_note",
    } <= names
