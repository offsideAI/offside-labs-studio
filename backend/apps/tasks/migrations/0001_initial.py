"""Initial migration for Task. Hand-authored."""

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
            name="Task",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("due_at", models.DateTimeField(blank=True, null=True)),
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
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("open", "Open"),
                            ("in_progress", "In progress"),
                            ("done", "Done"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="open",
                        max_length=16,
                    ),
                ),
                (
                    "priority",
                    models.CharField(
                        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
                        default="medium",
                        max_length=16,
                    ),
                ),
                ("custom", models.JSONField(blank=True, default=dict)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="tasks_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="owned_tasks",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "workspace",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tasks",
                        to="workspaces.workspace",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
            managers=[("objects", apps.workspaces.managers.WorkspaceScopedManager())],
        ),
        migrations.AddIndex(
            model_name="task",
            index=models.Index(
                fields=["workspace", "related_type", "related_id"],
                name="tasks_task_workspa_d4f1a3_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="task",
            index=models.Index(
                fields=["workspace", "owner", "status"], name="tasks_task_workspa_e5b2c4_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="task",
            index=models.Index(
                fields=["workspace", "due_at"], name="tasks_task_workspa_f6c3d5_idx"
            ),
        ),
    ]
