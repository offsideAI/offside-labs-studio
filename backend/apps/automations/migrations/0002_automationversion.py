"""M8: AutomationVersion — immutable graph snapshots.

- Adds `AutomationVersion` (workspace-scoped, unique on (automation, version_number)).
- Adds `Automation.published_version` FK (SET_NULL, nullable).
- Adds `AutomationRun.version` FK (PROTECT, nullable for M7 backward compat).
- Defaults `Automation.version` to 0 (no published version yet); the publish
  endpoint bumps it from 0 → 1, 1 → 2, ...
"""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import apps.workspaces.managers


class Migration(migrations.Migration):
    dependencies = [
        ("workspaces", "0001_initial"),
        ("automations", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AutomationVersion",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("version_number", models.IntegerField()),
                ("graph", models.JSONField()),
                ("trigger", models.JSONField(blank=True, default=dict)),
                ("published_at", models.DateTimeField(auto_now_add=True)),
                (
                    "automation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="versions",
                        to="automations.automation",
                    ),
                ),
                (
                    "published_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="automation_versions_published",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "workspace",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="automation_versions",
                        to="workspaces.workspace",
                    ),
                ),
            ],
            options={"ordering": ["-version_number"]},
            managers=[("objects", apps.workspaces.managers.WorkspaceScopedManager())],
        ),
        migrations.AddConstraint(
            model_name="automationversion",
            constraint=models.UniqueConstraint(
                fields=("automation", "version_number"),
                name="unique_automation_version_number",
            ),
        ),
        migrations.AddField(
            model_name="automation",
            name="published_version",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="automations.automationversion",
            ),
        ),
        migrations.AlterField(
            model_name="automation",
            name="version",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="automationrun",
            name="version",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="runs",
                to="automations.automationversion",
            ),
        ),
    ]
