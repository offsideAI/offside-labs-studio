"""Shared enums for polymorphic relations + activity kinds.

Tasks, Notes, and Activities all reference any of (contact, company, deal,
task, note) via a small `(related_type, related_id)` tuple. Using a small
enum + ID rather than ContentType avoids the GFK perf hit and makes
indexes straightforward.
"""

from __future__ import annotations

from django.db import models


class RelatedType(models.TextChoices):
    CONTACT = "contact", "Contact"
    COMPANY = "company", "Company"
    DEAL = "deal", "Deal"
    TASK = "task", "Task"
    NOTE = "note", "Note"


class ActivityKind(models.TextChoices):
    RECORD_CREATED = "record_created", "Record created"
    RECORD_UPDATED = "record_updated", "Record updated"
    FIELD_CHANGED = "field_changed", "Field changed"
    NOTE_ADDED = "note_added", "Note added"
    TASK_CREATED = "task_created", "Task created"
    TASK_COMPLETED = "task_completed", "Task completed"
    DEAL_STAGE_CHANGED = "deal_stage_changed", "Deal stage changed"
    EMAIL_SENT = "email_sent", "Email sent"
    EMAIL_RECEIVED = "email_received", "Email received"
    AI_ACTION = "ai_action", "AI action"
    AUTOMATION_RUN = "automation_run", "Automation run"


class ActorKind(models.TextChoices):
    USER = "user", "User"
    SYSTEM = "system", "System"
    AGENT = "agent", "Agent"
    AUTOMATION = "automation", "Automation"
