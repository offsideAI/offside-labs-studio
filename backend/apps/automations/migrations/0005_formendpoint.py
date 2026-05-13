"""M9.S1 phase 2c: FormEndpoint — public unsigned trigger row."""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import apps.workspaces.managers


class Migration(migrations.Migration):
    dependencies = [
        ("workspaces", "0001_initial"),
        ("automations", "0004_scheduletrigger"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="FormEndpoint",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("token", models.CharField(max_length=64, unique=True)),
                ("title", models.CharField(blank=True, max_length=200)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("rate_limit_per_minute", models.IntegerField(default=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("last_submission_at", models.DateTimeField(blank=True, null=True)),
                ("submission_count", models.IntegerField(default=0)),
                (
                    "automation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="form_endpoints",
                        to="automations.automation",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="form_endpoints_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "workspace",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="form_endpoints",
                        to="workspaces.workspace",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
            managers=[("objects", apps.workspaces.managers.WorkspaceScopedManager())],
        ),
        migrations.AddIndex(
            model_name="formendpoint",
            index=models.Index(
                fields=["workspace", "is_active"],
                name="automations_form_ws_c1a4b9_idx",
            ),
        ),
    ]
