"""Initial migration for Note. Hand-authored."""

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
            name="Note",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("body_md", models.TextField()),
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
                ("edit_log", models.JSONField(blank=True, default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="notes_authored",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "workspace",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notes",
                        to="workspaces.workspace",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
            managers=[("objects", apps.workspaces.managers.WorkspaceScopedManager())],
        ),
        migrations.AddIndex(
            model_name="note",
            index=models.Index(
                fields=["workspace", "related_type", "related_id"],
                name="notes_note_workspa_a7d4e9_idx",
            ),
        ),
    ]
