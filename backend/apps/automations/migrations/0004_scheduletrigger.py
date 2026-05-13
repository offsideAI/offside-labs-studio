"""M9.S1 phase 2b: ScheduleTrigger — cron-driven trigger row.

Beat scan task (`automations.scan_schedule_triggers`) walks active rows
every 60s and fires those whose cron expression is due since
`last_fired_at`.
"""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import apps.workspaces.managers


class Migration(migrations.Migration):
    dependencies = [
        ("workspaces", "0001_initial"),
        ("automations", "0003_webhookendpoint"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ScheduleTrigger",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("cron_expression", models.CharField(max_length=128)),
                ("timezone_name", models.CharField(default="UTC", max_length=64)),
                ("label", models.CharField(blank=True, max_length=120)),
                ("is_active", models.BooleanField(default=True)),
                ("last_fired_at", models.DateTimeField(blank=True, null=True)),
                ("fire_count", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "automation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="schedule_triggers",
                        to="automations.automation",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="schedule_triggers_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "workspace",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="schedule_triggers",
                        to="workspaces.workspace",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
            managers=[("objects", apps.workspaces.managers.WorkspaceScopedManager())],
        ),
        migrations.AddIndex(
            model_name="scheduletrigger",
            index=models.Index(
                fields=["is_active", "last_fired_at"],
                name="automations_sched_active_a4e2c1_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="scheduletrigger",
            index=models.Index(
                fields=["workspace", "is_active"],
                name="automations_sched_ws_b7f3d8_idx",
            ),
        ),
    ]
