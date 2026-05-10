"""Company — workspace-scoped record. Many-to-one parent for contacts."""

from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.workspaces.managers import WorkspaceScopedManager


class SizeBand(models.TextChoices):
    XS = "1-10", "1-10"
    S = "11-50", "11-50"
    M = "51-200", "51-200"
    L = "201-1000", "201-1000"
    XL = "1000+", "1000+"


class Company(models.Model):
    workspace = models.ForeignKey(
        "workspaces.Workspace",
        on_delete=models.CASCADE,
        related_name="companies",
    )
    name = models.CharField(max_length=200)
    domain = models.CharField(max_length=255, blank=True, db_index=True)
    size_band = models.CharField(max_length=16, choices=SizeBand.choices, blank=True)
    industry = models.CharField(max_length=100, blank=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_companies",
    )

    custom = models.JSONField(default=dict, blank=True)
    tags = models.JSONField(default=list, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="companies_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = WorkspaceScopedManager()

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["workspace", "domain"],
                condition=models.Q(domain__gt=""),
                name="unique_workspace_company_domain",
            ),
        ]
        indexes = [
            models.Index(fields=["workspace", "name"]),
        ]

    def __str__(self) -> str:
        return self.name
