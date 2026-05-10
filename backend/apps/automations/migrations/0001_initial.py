"""Initial migration for the workflow runtime. Hand-authored.

Models: Automation, AutomationRun, AutomationStepRun, HitlRequest, AgentPolicy.
"""

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import apps.workspaces.managers


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("workspaces", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Automation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("active", "Active"),
                            ("paused", "Paused"),
                            ("archived", "Archived"),
                        ],
                        default="draft",
                        max_length=16,
                    ),
                ),
                ("trigger", models.JSONField(blank=True, default=dict)),
                ("graph", models.JSONField(blank=True, default=dict)),
                ("version", models.IntegerField(default=1)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="automations_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "workspace",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="automations",
                        to="workspaces.workspace",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
            managers=[("objects", apps.workspaces.managers.WorkspaceScopedManager())],
        ),
        migrations.AddIndex(
            model_name="automation",
            index=models.Index(
                fields=["workspace", "status"], name="automations_workspa_a3b1c2_idx"
            ),
        ),
        migrations.CreateModel(
            name="AutomationRun",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("running", "Running"),
                            ("awaiting_approval", "Awaiting approval"),
                            ("awaiting_delay", "Awaiting delay"),
                            ("awaiting_event", "Awaiting event"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="pending",
                        max_length=24,
                    ),
                ),
                ("trigger_payload", models.JSONField(blank=True, default=dict)),
                ("current_step_id", models.CharField(blank=True, max_length=64)),
                ("state_snapshot", models.JSONField(blank=True, default=dict)),
                ("attempt", models.IntegerField(default=0)),
                ("resume_at", models.DateTimeField(blank=True, null=True)),
                ("awaiting_event_key", models.CharField(blank=True, max_length=255)),
                ("advancer_task_id", models.CharField(blank=True, max_length=64)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                (
                    "automation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="runs",
                        to="automations.automation",
                    ),
                ),
                (
                    "workspace",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="automation_runs",
                        to="workspaces.workspace",
                    ),
                ),
            ],
            options={"ordering": ["-id"]},
            managers=[("objects", apps.workspaces.managers.WorkspaceScopedManager())],
        ),
        migrations.AddIndex(
            model_name="automationrun",
            index=models.Index(
                fields=["workspace", "status"], name="automations_workspa_b4c2d3_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="automationrun",
            index=models.Index(
                fields=["status", "resume_at"], name="automations_status_c5d3e4_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="automationrun",
            index=models.Index(
                fields=["status", "awaiting_event_key"],
                name="automations_status_d6e4f5_idx",
            ),
        ),
        migrations.CreateModel(
            name="AutomationStepRun",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("step_id", models.CharField(max_length=64)),
                ("attempt", models.IntegerField(default=1)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("running", "Running"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                        ],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                ("input", models.JSONField(blank=True, default=dict)),
                ("output", models.JSONField(blank=True, default=dict)),
                ("model", models.CharField(blank=True, max_length=64)),
                ("cost_cents", models.IntegerField(default=0)),
                ("error", models.JSONField(blank=True, null=True)),
                ("idempotency_key", models.CharField(max_length=128, unique=True)),
                (
                    "run",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="step_runs",
                        to="automations.automationrun",
                    ),
                ),
            ],
            options={"ordering": ["-id"]},
        ),
        migrations.AddConstraint(
            model_name="automationsteprun",
            constraint=models.UniqueConstraint(
                fields=("run", "step_id", "attempt"), name="unique_run_step_attempt"
            ),
        ),
        migrations.CreateModel(
            name="HitlRequest",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("step_id", models.CharField(max_length=64)),
                ("summary", models.TextField()),
                ("payload", models.JSONField(blank=True, default=dict)),
                ("token", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("expires_at", models.DateTimeField()),
                ("decided_at", models.DateTimeField(blank=True, null=True)),
                (
                    "decision",
                    models.CharField(
                        blank=True,
                        choices=[("approve", "Approve"), ("reject", "Reject")],
                        max_length=16,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "decided_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="hitl_decisions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "run",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="hitl_requests",
                        to="automations.automationrun",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddIndex(
            model_name="hitlrequest",
            index=models.Index(
                fields=["run", "decided_at"], name="automations_run_id_e7f5a6_idx"
            ),
        ),
        migrations.CreateModel(
            name="AgentPolicy",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("action_type", models.CharField(max_length=64)),
                (
                    "mode",
                    models.CharField(
                        choices=[
                            ("suggest", "Suggest"),
                            ("approve", "Approve"),
                            ("autonomous", "Autonomous"),
                        ],
                        default="suggest",
                        max_length=16,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "workspace",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="agent_policies",
                        to="workspaces.workspace",
                    ),
                ),
            ],
            options={"ordering": ["action_type"]},
            managers=[("objects", apps.workspaces.managers.WorkspaceScopedManager())],
        ),
        migrations.AddConstraint(
            model_name="agentpolicy",
            constraint=models.UniqueConstraint(
                fields=("workspace", "action_type"), name="unique_workspace_agent_policy"
            ),
        ),
    ]
