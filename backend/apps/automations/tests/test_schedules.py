"""Schedule trigger tests (M9.S1 phase 2b).

We avoid freezing time. Instead we use cron expressions that are due
every minute ("* * * * *") and set `last_fired_at` to a point in the
past so `crontab.is_due()` returns True on the next sweep.
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.utils import timezone

from apps.automations.models import (
    Automation,
    AutomationRun,
    AutomationStatus,
    RunStatus,
    ScheduleTrigger,
)
from apps.automations.tasks import publish_automation, scan_schedule_triggers
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


def _published(workspace, user, *, status_=AutomationStatus.ACTIVE):  # type: ignore[no-untyped-def]
    a = Automation.objects.create(
        workspace=workspace,
        name="ScheduledFlow",
        graph=SIMPLE_GRAPH,
        trigger={"type": "schedule"},
        created_by=user,
    )
    publish_automation(a, user)
    a.refresh_from_db()
    if a.status != status_:
        a.status = status_
        a.save(update_fields=["status"])
    return a


def _schedule(
    workspace,
    automation,
    user,
    *,
    cron: str = "* * * * *",
    is_active: bool = True,
    last_fired_minutes_ago: int | None = 5,
) -> ScheduleTrigger:
    last = (
        timezone.now() - timedelta(minutes=last_fired_minutes_ago)
        if last_fired_minutes_ago is not None
        else None
    )
    return ScheduleTrigger.objects.create(
        workspace=workspace,
        automation=automation,
        cron_expression=cron,
        is_active=is_active,
        last_fired_at=last,
        created_by=user,
    )


@pytest.mark.django_db
def test_scan_fires_due_schedule(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    automation = _published(workspace, user)
    trigger = _schedule(workspace, automation, user, cron="* * * * *")

    fired = scan_schedule_triggers()

    assert fired == 1
    runs = list(AutomationRun.objects.filter(automation=automation))
    assert len(runs) == 1
    run = runs[0]
    assert run.status == RunStatus.COMPLETED
    assert run.version_id == automation.published_version_id
    assert run.trigger_payload["type"] == "schedule"
    assert run.trigger_payload["schedule_trigger_id"] == trigger.pk

    trigger.refresh_from_db()
    assert trigger.fire_count == 1
    assert trigger.last_fired_at is not None


@pytest.mark.django_db
def test_scan_skips_inactive_schedule(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    automation = _published(workspace, user)
    _schedule(workspace, automation, user, is_active=False)

    fired = scan_schedule_triggers()
    assert fired == 0
    assert AutomationRun.objects.filter(automation=automation).count() == 0


@pytest.mark.django_db
def test_scan_skips_recently_fired_schedule(workspace_user) -> None:  # type: ignore[no-untyped-def]
    """Daily cron at 9 AM with last_fired_at = 5 minutes ago → not due."""
    workspace, user = workspace_user
    automation = _published(workspace, user)
    _schedule(
        workspace,
        automation,
        user,
        cron="0 9 * * *",  # daily at 9am UTC
        last_fired_minutes_ago=5,
    )

    fired = scan_schedule_triggers()
    assert fired == 0
    assert AutomationRun.objects.filter(automation=automation).count() == 0


@pytest.mark.django_db
def test_scan_fires_for_paused_automation_but_no_run(workspace_user) -> None:  # type: ignore[no-untyped-def]
    """When the cron is due but the automation is paused, we still
    stamp last_fired_at so we don't backlog-fire on un-pause."""
    workspace, user = workspace_user
    automation = _published(workspace, user, status_=AutomationStatus.PAUSED)
    trigger = _schedule(workspace, automation, user, cron="* * * * *")

    fired = scan_schedule_triggers()
    # Sweep counted the trigger as due (1), but no run was created because
    # run_automation_with_payload returns None for non-ACTIVE.
    assert fired == 1
    assert AutomationRun.objects.filter(automation=automation).count() == 0

    trigger.refresh_from_db()
    assert trigger.fire_count == 1
    assert trigger.last_fired_at is not None


@pytest.mark.django_db
def test_scan_ignores_bad_cron(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    automation = _published(workspace, user)
    bad = _schedule(workspace, automation, user, cron="not a cron")
    good = _schedule(workspace, automation, user, cron="* * * * *")

    fired = scan_schedule_triggers()

    # Only the good cron fired; bad one was logged + skipped.
    assert fired == 1
    bad.refresh_from_db()
    good.refresh_from_db()
    assert bad.fire_count == 0
    assert good.fire_count == 1


@pytest.mark.django_db
def test_scan_returns_zero_when_no_triggers(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    _published(workspace, user)  # automation exists but no schedule rows
    assert scan_schedule_triggers() == 0


@pytest.mark.django_db
def test_multiple_schedules_on_same_automation_each_fire(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    automation = _published(workspace, user)
    _schedule(workspace, automation, user, cron="* * * * *")
    _schedule(workspace, automation, user, cron="* * * * *")

    fired = scan_schedule_triggers()
    assert fired == 2
    assert AutomationRun.objects.filter(automation=automation).count() == 2


@pytest.mark.django_db
def test_first_scan_fires_when_last_fired_is_null(workspace_user) -> None:  # type: ignore[no-untyped-def]
    workspace, user = workspace_user
    automation = _published(workspace, user)
    _schedule(workspace, automation, user, cron="* * * * *", last_fired_minutes_ago=None)

    fired = scan_schedule_triggers()
    assert fired == 1
    assert AutomationRun.objects.filter(automation=automation).count() == 1
