"""Initial migration for apps.ai — telemetry table for every LLM call."""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import apps.workspaces.managers


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("workspaces", "0001_initial"),
        ("automations", "0002_automationversion"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AICall",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("prompt_name", models.CharField(max_length=128)),
                ("model", models.CharField(max_length=64)),
                (
                    "status",
                    models.CharField(
                        choices=[("success", "Success"), ("error", "Error")],
                        default="success",
                        max_length=16,
                    ),
                ),
                ("tokens_in", models.IntegerField(default=0)),
                ("tokens_out", models.IntegerField(default=0)),
                ("cost_cents", models.IntegerField(default=0)),
                ("latency_ms", models.IntegerField(default=0)),
                ("step_id", models.CharField(blank=True, max_length=64)),
                ("error", models.TextField(blank=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "requested_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="ai_calls",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "run",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="ai_calls",
                        to="automations.automationrun",
                    ),
                ),
                (
                    "workspace",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ai_calls",
                        to="workspaces.workspace",
                    ),
                ),
            ],
            options={"ordering": ["-id"]},
            managers=[("objects", apps.workspaces.managers.WorkspaceScopedManager())],
        ),
        migrations.AddIndex(
            model_name="aicall",
            index=models.Index(
                fields=["workspace", "prompt_name", "-created_at"],
                name="ai_workspa_p_72a4f1_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="aicall",
            index=models.Index(
                fields=["workspace", "-created_at"], name="ai_workspa_c_8d3b22_idx"
            ),
        ),
    ]
