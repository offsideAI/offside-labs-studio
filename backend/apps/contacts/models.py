"""Contact — workspace-scoped record."""

from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.workspaces.managers import WorkspaceScopedManager


class LifecycleStage(models.TextChoices):
    LEAD = "lead", "Lead"
    QUALIFIED = "qualified", "Qualified"
    CUSTOMER = "customer", "Customer"
    CHURNED = "churned", "Churned"


class Contact(models.Model):
    workspace = models.ForeignKey(
        "workspaces.Workspace",
        on_delete=models.CASCADE,
        related_name="contacts",
    )

    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    primary_email = models.EmailField(blank=True, db_index=True)
    phones = models.JSONField(default=list, blank=True)
    title = models.CharField(max_length=200, blank=True)

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contacts",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_contacts",
    )

    lifecycle_stage = models.CharField(
        max_length=16, choices=LifecycleStage.choices, blank=True
    )
    source = models.CharField(max_length=100, blank=True)

    custom = models.JSONField(default=dict, blank=True)
    tags = models.JSONField(default=list, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="contacts_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = WorkspaceScopedManager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["workspace", "primary_email"]),
            models.Index(fields=["workspace", "last_name", "first_name"]),
        ]

    def __str__(self) -> str:
        full = f"{self.first_name} {self.last_name}".strip()
        return full or self.primary_email or f"Contact #{self.pk}"
