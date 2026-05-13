"""Models for the Agents Marketplace v1 (M9.S4 / FR-26).

`MarketplaceAgent` is the workspace-agnostic catalog row — no FK to
Workspace. The catalog is global + shareable; anyone can browse without
auth. `WorkspaceAgentInstall` is the per-workspace audit row created
each time someone installs an agent into their workspace; it FKs the
freshly-created `Automation`.

Installation flow (see views.MarketplaceAgentViewSet.install):
  1. Snapshot the agent's `graph` + `trigger` into a new `Automation`
     in the user's workspace.
  2. Immediately call `publish_automation` so an `AutomationVersion` is
     created and `Automation.status = ACTIVE`.
  3. Atomically bump `MarketplaceAgent.install_count` via `F("...") + 1`.
  4. Write the `WorkspaceAgentInstall` row.

Re-installing the same agent is allowed; each install creates a new
Automation row so the user can have multiple customised forks.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.workspaces.managers import WorkspaceScopedManager


class MarketplaceAgentCategory(models.TextChoices):
    LEAD_MANAGEMENT = "lead_management", "Lead management"
    DEAL_HYGIENE = "deal_hygiene", "Deal hygiene"
    COMMS = "comms", "Communications"
    INTEGRATIONS = "integrations", "Integrations"
    OPERATIONS = "operations", "Operations"


class MarketplaceAgent(models.Model):
    """A curated, workspace-agnostic workflow template.

    `graph` + `trigger` are JSON snapshots in the same shape the rest of
    the M8/M9 runtime expects. Install copies them verbatim into a new
    `Automation` row + immediately publishes a version, so the user
    lands on an editable, runnable workflow.
    """

    slug = models.SlugField(max_length=80, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    long_description = models.TextField(blank=True)

    category = models.CharField(
        max_length=64,
        choices=MarketplaceAgentCategory.choices,
        default=MarketplaceAgentCategory.OPERATIONS,
    )
    icon_emoji = models.CharField(max_length=8, default="🤖")
    author = models.CharField(max_length=200, default="Offside Labs")

    graph = models.JSONField()
    trigger = models.JSONField(default=dict, blank=True)

    install_count = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-install_count", "name"]
        indexes = [
            models.Index(fields=["is_published", "category"]),
            models.Index(fields=["is_published", "-install_count"]),
        ]

    def __str__(self) -> str:
        return f"{self.icon_emoji} {self.name}"


class WorkspaceAgentInstall(models.Model):
    """Audit row written each time an agent is installed into a workspace."""

    workspace = models.ForeignKey(
        "workspaces.Workspace",
        on_delete=models.CASCADE,
        related_name="agent_installs",
    )
    marketplace_agent = models.ForeignKey(
        MarketplaceAgent,
        on_delete=models.PROTECT,
        related_name="installs",
    )
    automation = models.ForeignKey(
        "automations.Automation",
        on_delete=models.CASCADE,
        related_name="marketplace_installs",
    )
    installed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="marketplace_installs",
    )
    installed_at = models.DateTimeField(auto_now_add=True)

    objects = WorkspaceScopedManager()

    class Meta:
        ordering = ["-installed_at"]
        indexes = [
            models.Index(fields=["workspace", "-installed_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.workspace.slug} installed {self.marketplace_agent.slug}"
