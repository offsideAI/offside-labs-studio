"""M9.S4 phase 1: Agents Marketplace v1 (FR-26) — initial models.

- `MarketplaceAgent` is workspace-agnostic (global catalog).
- `WorkspaceAgentInstall` audits per-workspace installs, FKs the
  Automation that was created on install.
"""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import apps.workspaces.managers


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("workspaces", "0001_initial"),
        ("automations", "0005_formendpoint"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="MarketplaceAgent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("slug", models.SlugField(max_length=80, unique=True)),
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField()),
                ("long_description", models.TextField(blank=True)),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("lead_management", "Lead management"),
                            ("deal_hygiene", "Deal hygiene"),
                            ("comms", "Communications"),
                            ("integrations", "Integrations"),
                            ("operations", "Operations"),
                        ],
                        default="operations",
                        max_length=64,
                    ),
                ),
                ("icon_emoji", models.CharField(default="🤖", max_length=8)),
                ("author", models.CharField(default="Offside Labs", max_length=200)),
                ("graph", models.JSONField()),
                ("trigger", models.JSONField(blank=True, default=dict)),
                ("install_count", models.IntegerField(default=0)),
                ("is_published", models.BooleanField(default=True)),
                ("published_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["-install_count", "name"]},
        ),
        migrations.AddIndex(
            model_name="marketplaceagent",
            index=models.Index(
                fields=["is_published", "category"], name="marketplac_pub_cat_a1f5d2_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="marketplaceagent",
            index=models.Index(
                fields=["is_published", "-install_count"],
                name="marketplac_pub_inst_b3c4e8_idx",
            ),
        ),
        migrations.CreateModel(
            name="WorkspaceAgentInstall",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("installed_at", models.DateTimeField(auto_now_add=True)),
                (
                    "automation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="marketplace_installs",
                        to="automations.automation",
                    ),
                ),
                (
                    "installed_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="marketplace_installs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "marketplace_agent",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="installs",
                        to="marketplace.marketplaceagent",
                    ),
                ),
                (
                    "workspace",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="agent_installs",
                        to="workspaces.workspace",
                    ),
                ),
            ],
            options={"ordering": ["-installed_at"]},
            managers=[("objects", apps.workspaces.managers.WorkspaceScopedManager())],
        ),
        migrations.AddIndex(
            model_name="workspaceagentinstall",
            index=models.Index(
                fields=["workspace", "-installed_at"],
                name="marketplac_ws_dt_c8a9f1_idx",
            ),
        ),
    ]
