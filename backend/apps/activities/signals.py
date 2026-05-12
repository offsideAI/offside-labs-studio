"""Signal handlers that fire Activity rows on Contact/Company/Deal save.

Also wires the record trigger (M9.S1) — every record event dispatches
to `apps.automations.triggers.emit_record` via `transaction.on_commit`
so automations only fire after the user's transaction commits.

Tasks and Notes are handled inline in their own apps' save flows so the
signal handler has access to actor info that's not on the model itself.
"""

from __future__ import annotations

from typing import Any

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.automations.triggers import emit_record
from apps.companies.models import Company
from apps.contacts.models import Contact
from apps.deals.models import Deal

from .models import Activity
from .types import ActivityKind, RelatedType


def _record_activity(
    workspace,  # type: ignore[no-untyped-def]
    kind: str,
    related_type: str,
    related_id: int,
    actor_user_id: int | None,
    payload: dict[str, Any] | None = None,
) -> None:
    Activity.objects.create(
        workspace=workspace,
        kind=kind,
        actor_user_id=actor_user_id,
        related_type=related_type,
        related_id=related_id,
        payload=payload or {},
    )


def _emit_record_after_commit(
    *,
    workspace_id: int,
    entity_type: str,
    event: str,
    record_id: int,
    payload: dict[str, Any],
) -> None:
    """Schedule a record-trigger dispatch for after the current transaction
    commits. If we're not in an atomic block, `on_commit` runs the lambda
    synchronously, which is fine.
    """
    transaction.on_commit(
        lambda: emit_record(
            workspace_id=workspace_id,
            entity_type=entity_type,
            event=event,
            record_id=record_id,
            payload=payload,
        )
    )


@receiver(post_save, sender=Contact)
def contact_saved(sender, instance: Contact, created: bool, **kwargs: Any) -> None:
    if not created:
        return
    payload = {"name": str(instance), "primary_email": instance.primary_email}
    _record_activity(
        workspace=instance.workspace,
        kind=ActivityKind.RECORD_CREATED,
        related_type=RelatedType.CONTACT,
        related_id=instance.id,
        actor_user_id=instance.created_by_id,
        payload=payload,
    )
    _emit_record_after_commit(
        workspace_id=instance.workspace_id,
        entity_type="contact",
        event="created",
        record_id=instance.id,
        payload=payload,
    )


@receiver(post_save, sender=Company)
def company_saved(sender, instance: Company, created: bool, **kwargs: Any) -> None:
    if not created:
        return
    payload = {"name": instance.name, "domain": instance.domain}
    _record_activity(
        workspace=instance.workspace,
        kind=ActivityKind.RECORD_CREATED,
        related_type=RelatedType.COMPANY,
        related_id=instance.id,
        actor_user_id=instance.created_by_id,
        payload=payload,
    )
    _emit_record_after_commit(
        workspace_id=instance.workspace_id,
        entity_type="company",
        event="created",
        record_id=instance.id,
        payload=payload,
    )


@receiver(post_save, sender=Deal)
def deal_saved(sender, instance: Deal, created: bool, **kwargs: Any) -> None:
    if created:
        payload = {
            "name": instance.name,
            "stage_id": instance.stage_id,
            "value_cents": instance.value_cents,
        }
        _record_activity(
            workspace=instance.workspace,
            kind=ActivityKind.RECORD_CREATED,
            related_type=RelatedType.DEAL,
            related_id=instance.id,
            actor_user_id=instance.created_by_id,
            payload=payload,
        )
        _emit_record_after_commit(
            workspace_id=instance.workspace_id,
            entity_type="deal",
            event="created",
            record_id=instance.id,
            payload=payload,
        )
        return

    # Detect stage changes via update_fields when the caller passes them
    # (best-effort). For richer field-changed events we'll instrument the
    # ViewSet's perform_update in M5+ to compute diffs.
    update_fields = kwargs.get("update_fields") or set()
    if "stage_id" in update_fields:
        payload = {"stage_id": instance.stage_id}
        _record_activity(
            workspace=instance.workspace,
            kind=ActivityKind.DEAL_STAGE_CHANGED,
            related_type=RelatedType.DEAL,
            related_id=instance.id,
            actor_user_id=None,  # actor flows through view-level instrumentation later
            payload=payload,
        )
        _emit_record_after_commit(
            workspace_id=instance.workspace_id,
            entity_type="deal",
            event="stage_changed",
            record_id=instance.id,
            payload=payload,
        )
