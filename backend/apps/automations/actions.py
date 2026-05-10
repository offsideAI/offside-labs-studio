"""Action handler registry.

Handlers are pure side-effecting functions: `(workspace, input) -> output`.
The run advancer wraps every call in a per-step idempotency check, so
the handler itself does NOT need to short-circuit on duplicate execution
— the framework does that one layer up via AutomationStepRun.

To register an action:

    @register("crm.move_deal_stage")
    def move_deal_stage(workspace, payload):
        ...
        return {"deal_id": ..., "stage_id": ...}

M9 expands the registry; M11 lands AI-prompt actions.
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from .exceptions import ActionError

ActionHandler = Callable[[Any, dict[str, Any]], dict[str, Any]]

_REGISTRY: dict[str, ActionHandler] = {}

log = logging.getLogger("apps.automations.actions")


def register(name: str) -> Callable[[ActionHandler], ActionHandler]:
    def decorator(fn: ActionHandler) -> ActionHandler:
        if name in _REGISTRY:
            raise ValueError(f"duplicate action: {name}")
        _REGISTRY[name] = fn
        return fn

    return decorator


def get(name: str) -> ActionHandler:
    try:
        return _REGISTRY[name]
    except KeyError as exc:
        raise ActionError(f"unknown action: {name!r}") from exc


def all_names() -> list[str]:
    return sorted(_REGISTRY)


# --- Built-in actions ---


@register("noop")
def action_noop(workspace, payload: dict[str, Any]) -> dict[str, Any]:
    """Returns the payload unchanged. Useful for graph traversal tests."""
    return dict(payload)


@register("log")
def action_log(workspace, payload: dict[str, Any]) -> dict[str, Any]:
    """Logs the payload at info. Returns it for downstream branching."""
    log.info("workflow.log workspace=%s payload=%s", getattr(workspace, "slug", "?"), payload)
    return dict(payload)


@register("crm.create_contact")
def action_create_contact(workspace, payload: dict[str, Any]) -> dict[str, Any]:
    """Creates a Contact in the active workspace. Requires `created_by_id` in payload."""
    from apps.contacts.models import Contact

    if "created_by_id" not in payload:
        raise ActionError("crm.create_contact requires created_by_id")

    contact = Contact.objects.create(
        workspace=workspace,
        first_name=payload.get("first_name", ""),
        last_name=payload.get("last_name", ""),
        primary_email=payload.get("primary_email", ""),
        title=payload.get("title", ""),
        lifecycle_stage=payload.get("lifecycle_stage", ""),
        source=payload.get("source", ""),
        custom=payload.get("custom", {}),
        created_by_id=payload["created_by_id"],
    )
    return {"contact_id": contact.id, "primary_email": contact.primary_email}


@register("crm.move_deal_stage")
def action_move_deal_stage(workspace, payload: dict[str, Any]) -> dict[str, Any]:
    from apps.deals.models import Deal

    if "deal_id" not in payload or "stage_id" not in payload:
        raise ActionError("crm.move_deal_stage requires deal_id and stage_id")

    deal = Deal.objects.get(workspace=workspace, pk=payload["deal_id"])
    deal.stage_id = payload["stage_id"]
    deal.save(update_fields=["stage_id"])
    return {"deal_id": deal.id, "stage_id": deal.stage_id}
