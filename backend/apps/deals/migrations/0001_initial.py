"""Initial migration for Pipeline + Deal. Hand-authored."""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import apps.deals.models
import apps.workspaces.managers


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("workspaces", "0001_initial"),
        ("contacts", "0001_initial"),
        ("companies", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Pipeline",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=120)),
                ("stages", models.JSONField(blank=True, default=apps.deals.models.default_pipeline_stages)),
                ("is_default", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="pipelines_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "workspace",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="pipelines",
                        to="workspaces.workspace",
                    ),
                ),
            ],
            options={"ordering": ["name"]},
            managers=[("objects", apps.workspaces.managers.WorkspaceScopedManager())],
        ),
        migrations.AddConstraint(
            model_name="pipeline",
            constraint=models.UniqueConstraint(
                fields=("workspace", "name"), name="unique_workspace_pipeline_name"
            ),
        ),
        migrations.CreateModel(
            name="Deal",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("stage_id", models.CharField(db_index=True, max_length=64)),
                ("value_cents", models.BigIntegerField(default=0)),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("expected_close", models.DateField(blank=True, null=True)),
                ("custom", models.JSONField(blank=True, default=dict)),
                ("tags", models.JSONField(blank=True, default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                (
                    "company",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="deals",
                        to="companies.company",
                    ),
                ),
                (
                    "contact",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="deals",
                        to="contacts.contact",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="deals_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="owned_deals",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "pipeline",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="deals",
                        to="deals.pipeline",
                    ),
                ),
                (
                    "workspace",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="deals",
                        to="workspaces.workspace",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
            managers=[("objects", apps.workspaces.managers.WorkspaceScopedManager())],
        ),
        migrations.AddIndex(
            model_name="deal",
            index=models.Index(
                fields=["workspace", "pipeline", "stage_id"],
                name="deals_deal_workspa_d6b2af_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="deal",
            index=models.Index(
                fields=["workspace", "owner"],
                name="deals_deal_workspa_e7c3b0_idx",
            ),
        ),
    ]
