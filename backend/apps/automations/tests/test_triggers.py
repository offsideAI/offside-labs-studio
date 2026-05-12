"""Trigger dispatcher + record-trigger tests (M9.S1 phase 1).

Celery runs eager in tests (per backend/conftest.py), and
`transaction.on_commit` callbacks fire when the outer transaction
commits. pytest-django wraps every test in an atomic block by default
— we use the `transaction=True` flag where needed so commits actually
happen.
"""

from __future__ import annotations

import pytest
from django.db import transaction

from apps.automations.models import (
    Automation,
    AutomationRun,
    AutomationStatus,
    RunStatus,
)
from apps.automations.tasks import publish_automation
from apps.automations.triggers import (
    TriggerEvent,
    emit_record,
    fire,
)
from apps.companies.models import Company
from apps.contacts.models import Contact
from apps.deals.models import Deal, Pipeline, default_pipeline_stages
from apps.users.models import User
from apps.workspaces.models import Workspace


SIMPLE_GRAPH = {
    "start_node_id": "n1",
    "nodes": {
        "n1": {
            "type": "action",
            "config": {"action": "noop", "input": {"ok": True}},
            "next": "end",
        },
        "end": {"type": "end"},
    },
}


@pytest.fixture
def workspace_user(db):  # type: ignore[no-untyped-def]
    user = User.objects.create_user(email="owner@example.com", password="VerySecurePass123!")
    workspace = Workspace.objects.create(name="Acme", slug="acme", created_by=user)
    return workspace, user


def _published_automation(
    workspace: Workspace,
    user: User,
    *,
    trigger: dict | None = None,
    status: str = AutomationStatus.ACTIVE,
) -> Automation:
    a = Automation.objects.create(
        workspace=workspace,
        name="Trigger test",
        graph=SIMPLE_GRAPH,
        trigger=trigger or {"type": "manual"},
        created_by=user,
    )
    publish_automation(a, user)
    a.refresh_from_db()
    if a.status != status:
        a.status = status
        a.save(update_fields=["status"])
    return a


@pytest.mark.django_db
def test_fire_matches_record_trigger(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    automation = _published_automation(
        workspace,
        user,
        trigger={"type": "record", "entity_type": "contact", "event": "created"},
    )

    event = TriggerEvent(
        type="record",
        workspace_id=workspace.id,
        entity_type="contact",
        event="created",
        record_id=42,
        payload={"name": "Ada"},
    )
    run_ids = fire(event)

    assert len(run_ids) == 1
    run = AutomationRun.objects.get(pk=run_ids[0])
    assert run.automation_id == automation.id
    assert run.version_id == automation.published_version_id
    assert run.status == RunStatus.COMPLETED  # noop graph runs synchronously
    assert run.trigger_payload["entity_type"] == "contact"
    assert run.trigger_payload["record_id"] == 42
    assert run.trigger_payload["name"] == "Ada"


@pytest.mark.django_db
def test_fire_does_not_match_wrong_entity(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    _published_automation(
        workspace,
        user,
        trigger={"type": "record", "entity_type": "company", "event": "created"},
    )

    event = TriggerEvent(
        type="record",
        workspace_id=workspace.id,
        entity_type="contact",
        event="created",
        record_id=1,
    )
    assert fire(event) == []


@pytest.mark.django_db
def test_fire_does_not_match_wrong_event(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    _published_automation(
        workspace,
        user,
        trigger={"type": "record", "entity_type": "deal", "event": "stage_changed"},
    )

    event = TriggerEvent(
        type="record",
        workspace_id=workspace.id,
        entity_type="deal",
        event="created",
        record_id=1,
    )
    assert fire(event) == []


@pytest.mark.django_db
def test_fire_skips_draft_automations(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    # Draft (never published) — should never fire.
    Automation.objects.create(
        workspace=workspace,
        name="Draft",
        graph=SIMPLE_GRAPH,
        trigger={"type": "record", "entity_type": "contact", "event": "created"},
        created_by=user,
    )

    event = TriggerEvent(
        type="record",
        workspace_id=workspace.id,
        entity_type="contact",
        event="created",
        record_id=1,
    )
    assert fire(event) == []


@pytest.mark.django_db
def test_fire_respects_workspace_isolation(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    other_user = User.objects.create_user(email="other@example.com", password="VerySecurePass123!")
    other_ws = Workspace.objects.create(name="Other", slug="other", created_by=other_user)
    # Automation in OTHER workspace with a matching trigger.
    _published_automation(
        other_ws,
        other_user,
        trigger={"type": "record", "entity_type": "contact", "event": "created"},
    )

    event = TriggerEvent(
        type="record",
        workspace_id=workspace.id,
        entity_type="contact",
        event="created",
        record_id=1,
    )
    assert fire(event) == []


@pytest.mark.django_db
def test_manual_trigger_never_auto_fires(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    _published_automation(workspace, user, trigger={"type": "manual"})

    event = TriggerEvent(type="manual", workspace_id=workspace.id)
    assert fire(event) == []


@pytest.mark.django_db
def test_emit_record_validates_inputs(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, _ = workspace_user
    with pytest.raises(ValueError):
        emit_record(
            workspace_id=workspace.id,
            entity_type="totally-unknown",  # type: ignore[arg-type]
            event="created",
            record_id=1,
        )
    with pytest.raises(ValueError):
        emit_record(
            workspace_id=workspace.id,
            entity_type="contact",
            event="not-a-real-event",  # type: ignore[arg-type]
            record_id=1,
        )


@pytest.mark.django_db(transaction=True)
def test_contact_save_fires_record_trigger(workspace_user) -> None:  # type: ignore[no-untyped-def]
    """End-to-end: saving a Contact should kick off any automation
    whose trigger matches `{type: record, entity_type: contact, event:
    created}`. We need `transaction=True` so on_commit fires.
    """
    workspace, user = workspace_user
    automation = _published_automation(
        workspace,
        user,
        trigger={"type": "record", "entity_type": "contact", "event": "created"},
    )

    Contact.objects.create(
        workspace=workspace,
        first_name="Ada",
        last_name="Lovelace",
        primary_email="ada@example.com",
        created_by=user,
    )

    runs = list(AutomationRun.objects.filter(automation=automation))
    assert len(runs) == 1
    assert runs[0].status == RunStatus.COMPLETED


@pytest.mark.django_db(transaction=True)
def test_deal_stage_change_fires_record_trigger(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    automation = _published_automation(
        workspace,
        user,
        trigger={"type": "record", "entity_type": "deal", "event": "stage_changed"},
    )

    pipeline = Pipeline.objects.create(
        workspace=workspace,
        name="Default",
        stages=default_pipeline_stages(),
        is_default=True,
        created_by=user,
    )
    deal = Deal.objects.create(
        workspace=workspace,
        name="Acme deal",
        pipeline=pipeline,
        stage_id="lead",
        value_cents=10000,
        currency="USD",
        created_by=user,
    )
    # Initial create → fires `created` event, not `stage_changed`.
    runs_after_create = list(AutomationRun.objects.filter(automation=automation))
    assert runs_after_create == []

    deal.stage_id = "qualified"
    deal.save(update_fields=["stage_id"])

    runs = list(AutomationRun.objects.filter(automation=automation))
    assert len(runs) == 1
    assert runs[0].trigger_payload["event"] == "stage_changed"
    assert runs[0].trigger_payload["stage_id"] == "qualified"


@pytest.mark.django_db(transaction=True)
def test_company_save_fires_record_trigger(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    automation = _published_automation(
        workspace,
        user,
        trigger={"type": "record", "entity_type": "company", "event": "created"},
    )

    Company.objects.create(
        workspace=workspace,
        name="Acme Co",
        domain="acme.example",
        created_by=user,
    )

    runs = list(AutomationRun.objects.filter(automation=automation))
    assert len(runs) == 1
    assert runs[0].trigger_payload["entity_type"] == "company"
