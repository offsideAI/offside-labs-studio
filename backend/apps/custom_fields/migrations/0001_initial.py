"""Initial migration for CustomFieldDef. Hand-authored."""

import django.db.models.deletion
from django.db import migrations, models

import apps.workspaces.managers


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("workspaces", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomFieldDef",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "entity_type",
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
                ("key", models.SlugField(max_length=64)),
                ("label", models.CharField(max_length=120)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("text", "Text"),
                            ("long_text", "Long text"),
                            ("number", "Number"),
                            ("select", "Select"),
                            ("multi_select", "Multi-select"),
                            ("date", "Date"),
                            ("datetime", "Datetime"),
                            ("boolean", "Boolean"),
                            ("url", "URL"),
                            ("email", "Email"),
                            ("phone", "Phone"),
                            ("relation", "Relation"),
                        ],
                        max_length=16,
                    ),
                ),
                ("options", models.JSONField(blank=True, default=list)),
                ("required", models.BooleanField(default=False)),
                ("indexed", models.BooleanField(default=False)),
                ("order", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "workspace",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="custom_field_defs",
                        to="workspaces.workspace",
                    ),
                ),
            ],
            options={"ordering": ["entity_type", "order", "key"]},
            managers=[("objects", apps.workspaces.managers.WorkspaceScopedManager())],
        ),
        migrations.AddConstraint(
            model_name="customfielddef",
            constraint=models.UniqueConstraint(
                fields=("workspace", "entity_type", "key"),
                name="unique_workspace_entity_field_key",
            ),
        ),
    ]
