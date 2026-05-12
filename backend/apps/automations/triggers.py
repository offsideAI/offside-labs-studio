"""Trigger dispatcher (M9.S1).

A trigger is a small declarative config attached to an `Automation` via
its `trigger` JSON field. When something happens in the system that
might match a trigger — a Contact is saved, a webhook is received,
Beat fires a cron — the relevant code path builds a `TriggerEvent`
and calls `fire(event)`. We look up every ACTIVE automation with a
published version in the same workspace, run `_matches(...)` against
each automation's trigger config, and `kick_off(run)` for every match.

Trigger types (v1):

  manual       — never auto-fires; only the editor's start_run endpoint
                 creates runs. Default for new workflows.

  record       — fires when a CRM record is created / updated / stage-
                 changed. Config:
                   { type: "record",
                     entity_type: "contact" | "company" | "deal",
                     event: "created" | "updated" | "stage_changed" }

  webhook      — TBD (phase 2 of M9.S1).
  schedule     — TBD (phase 2 of M9.S1).
  form         — TBD (phase 2 of M9.S1).
  ai_condition — TBD (phase 2 of M9.S1).

Dispatch must happen AFTER the DB transaction that produced the event
has committed — otherwise a rollback would leave us running an
automation against state the user never persisted. Callers use
`django.db.transaction.on_commit(lambda: fire(event))` to chain. See
`apps.activities.signals` for the canonical wiring.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from .models import (
    Automation,
    AutomationRun,
    AutomationStatus,
)
from .tasks import kick_off

log = logging.getLogger("apps.automations.triggers")


# Supported trigger types. Add new ones here as they ship.
TRIGGER_TYPES = ("manual", "record", "webhook", "schedule", "form", "ai_condition")

# Record-trigger events. These map 1:1 with `apps.activities.types.ActivityKind`
# values, but are duplicated here so the trigger config schema doesn't have to
# import the activities app.
RECORD_EVENTS = ("created", "updated", "stage_changed")
RECORD_ENTITY_TYPES = ("contact", "company", "deal")


@dataclass
class TriggerEvent:
    type: str
    workspace_id: int
    entity_type: str | None = None
    event: str | None = None
    record_id: int | None = None
    payload: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.type not in TRIGGER_TYPES:
            raise ValueError(f"unknown trigger type {self.type!r}")


def fire(event: TriggerEvent) -> list[int]:
    """Find every active, published automation whose trigger matches the
    event and create + kick off an AutomationRun for each. Returns the
    list of created run ids (mostly useful for tests + telemetry).
    """
    qs = Automation.objects.filter(
        workspace_id=event.workspace_id,
        status=AutomationStatus.ACTIVE,
        published_version__isnull=False,
    ).only("id", "trigger", "published_version_id", "workspace_id")

    run_ids: list[int] = []
    for automation in qs:
        if not _matches(automation.trigger or {}, event):
            continue
        run = AutomationRun.objects.create(
            automation_id=automation.id,
            workspace_id=automation.workspace_id,
            version_id=automation.published_version_id,
            trigger_payload=_payload_for(event),
        )
        kick_off(run)
        run_ids.append(run.id)
    if run_ids:
        log.info(
            "trigger fire: type=%s workspace=%s matched %d run(s) %s",
            event.type,
            event.workspace_id,
            len(run_ids),
            run_ids,
        )
    return run_ids


def _matches(trigger_config: dict[str, Any], event: TriggerEvent) -> bool:
    if trigger_config.get("type") != event.type:
        return False
    if event.type == "manual":
        # Manual never auto-fires. The start_run endpoint creates runs directly.
        return False
    if event.type == "record":
        if trigger_config.get("entity_type") != event.entity_type:
            return False
        if trigger_config.get("event") != event.event:
            return False
        return True
    # Other types: phase-2 of M9.S1.
    return False


def _payload_for(event: TriggerEvent) -> dict[str, Any]:
    """The trigger_payload stored on AutomationRun. Includes the event
    type + entity + id so step templates can reference it as
    `{{ trigger.entity_type }}` once we add `trigger` to the template
    state (planned for M9.S2)."""
    base: dict[str, Any] = {
        "type": event.type,
        "entity_type": event.entity_type,
        "event": event.event,
        "record_id": event.record_id,
    }
    base.update(event.payload or {})
    return base


# --- Convenience emitters (use these from signal handlers / views) -------------


def emit_record(
    *,
    workspace_id: int,
    entity_type: str,
    event: str,
    record_id: int,
    payload: dict[str, Any] | None = None,
) -> list[int]:
    """Build + fire a record-trigger event. Validates inputs."""
    if entity_type not in RECORD_ENTITY_TYPES:
        raise ValueError(f"unknown record entity_type {entity_type!r}")
    if event not in RECORD_EVENTS:
        raise ValueError(f"unknown record event {event!r}")
    return fire(
        TriggerEvent(
            type="record",
            workspace_id=workspace_id,
            entity_type=entity_type,
            event=event,
            record_id=record_id,
            payload=payload or {},
        )
    )


__all__ = [
    "TriggerEvent",
    "TRIGGER_TYPES",
    "RECORD_EVENTS",
    "RECORD_ENTITY_TYPES",
    "fire",
    "emit_record",
]
