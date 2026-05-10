"""Initial migration for Activity. Hand-authored."""

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
            name="Activity",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "kind",
                    models.CharField(
                        choices=[
                            ("record_created", "Record created"),
                            ("record_updated", "Record updated"),
                            ("field_changed", "Field changed"),
                            ("note_added", "Note added"),
                            ("task_created", "Task created"),
                            ("task_completed", "Task completed"),
                            ("deal_stage_changed", "Deal stage changed"),
                            ("email_sent", "Email sent"),
                            ("email_received", "Email received"),
                            ("ai_action", "AI action"),
                            ("automation_run", "Automation run"),
                        ],
                        max_length=32,
                    ),
                ),
                (
                    "actor_kind",
                    models.CharField(
                        choices=[
                            ("user", "User"),
                            ("system", "System"),
                            ("agent", "Agent"),
                            ("automation", "Automation"),
                        ],
                        default="user",
                        max_length=16,
                    ),
                ),
                (
                    "related_type",
                    models.CharField(
                        choices=[
                            ("contact", "Contact"),
                            ("company", "Company"),
                            ("deal", "Deal"),
                            ("task", "Task"),
                            ("note", "Note"),
                        ],
                        max_length=16,
                    ),
                ),
                ("related_id", models.BigIntegerField()),
                ("payload", models.JSONField(blank=True, default=dict)),
                ("occurred_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                (
                    "actor_user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="activities",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "workspace",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="activities",
                        to="workspaces.workspace",
                    ),
                ),
            ],
            options={"ordering": ["-occurred_at"]},
            managers=[("objects", apps.workspaces.managers.WorkspaceScopedManager())],
        ),
        migrations.AddIndex(
            model_name="activity",
            index=models.Index(
                fields=["workspace", "related_type", "related_id", "-occurred_at"],
                name="activities__workspa_a3b1c2_idx",
            ),
        ),
    ]
