"""CustomFieldDef — workspace-scoped, per-entity-type custom field metadata.

Custom field values themselves live in the JSONB `custom` column on each
entity (Contact, Company, Deal, Task, Note). This model stores the schema:
which keys exist, what types they have, what options the selects use.
"""

from __future__ import annotations

from django.db import models

from apps.workspaces.managers import WorkspaceScopedManager


class EntityType(models.TextChoices):
    CONTACT = "contact", "Contact"
    COMPANY = "company", "Company"
    DEAL = "deal", "Deal"
    TASK = "task", "Task"
    NOTE = "note", "Note"


class FieldType(models.TextChoices):
    TEXT = "text", "Text"
    LONG_TEXT = "long_text", "Long text"
    NUMBER = "number", "Number"
    SELECT = "select", "Select"
    MULTI_SELECT = "multi_select", "Multi-select"
    DATE = "date", "Date"
    DATETIME = "datetime", "Datetime"
    BOOLEAN = "boolean", "Boolean"
    URL = "url", "URL"
    EMAIL = "email", "Email"
    PHONE = "phone", "Phone"
    RELATION = "relation", "Relation"


class CustomFieldDef(models.Model):
    workspace = models.ForeignKey(
        "workspaces.Workspace",
        on_delete=models.CASCADE,
        related_name="custom_field_defs",
    )
    entity_type = models.CharField(max_length=16, choices=EntityType.choices)
    key = models.SlugField(max_length=64)
    label = models.CharField(max_length=120)
    type = models.CharField(max_length=16, choices=FieldType.choices)
    options = models.JSONField(default=list, blank=True)
    required = models.BooleanField(default=False)
    indexed = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = WorkspaceScopedManager()

    class Meta:
        ordering = ["entity_type", "order", "key"]
        constraints = [
            models.UniqueConstraint(
                fields=["workspace", "entity_type", "key"],
                name="unique_workspace_entity_field_key",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.entity_type}.{self.key} ({self.type})"
