"""M9.S1 phase 2a: WebhookEndpoint — public-URL trigger for an automation.

Each row mints a token (path component of the public URL) and a secret
(used to verify `X-Offside-Signature: sha256=<hex>` over the raw body).
"""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import apps.workspaces.managers


class Migration(migrations.Migration):
    dependencies = [
        ("workspaces", "0001_initial"),
        ("automations", "0002_automationversion"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="WebhookEndpoint",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("token", models.CharField(max_length=64, unique=True)),
                ("secret", models.CharField(max_length=128)),
                ("label", models.CharField(blank=True, max_length=120)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("last_fired_at", models.DateTimeField(blank=True, null=True)),
                ("fire_count", models.IntegerField(default=0)),
                (
                    "automation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="webhook_endpoints",
                        to="automations.automation",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="webhook_endpoints_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "workspace",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="webhook_endpoints",
                        to="workspaces.workspace",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
            managers=[("objects", apps.workspaces.managers.WorkspaceScopedManager())],
        ),
        migrations.AddIndex(
            model_name="webhookendpoint",
            index=models.Index(
                fields=["workspace", "is_active"], name="automations_wh_active_5e9c14_idx"
            ),
        ),
    ]
