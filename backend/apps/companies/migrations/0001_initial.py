"""Initial migration for Company. Hand-authored."""

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
            name="Company",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("domain", models.CharField(blank=True, db_index=True, max_length=255)),
                (
                    "size_band",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("1-10", "1-10"),
                            ("11-50", "11-50"),
                            ("51-200", "51-200"),
                            ("201-1000", "201-1000"),
                            ("1000+", "1000+"),
                        ],
                        max_length=16,
                    ),
                ),
                ("industry", models.CharField(blank=True, max_length=100)),
                ("custom", models.JSONField(blank=True, default=dict)),
                ("tags", models.JSONField(blank=True, default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="companies_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="owned_companies",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "workspace",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="companies",
                        to="workspaces.workspace",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
            managers=[("objects", apps.workspaces.managers.WorkspaceScopedManager())],
        ),
        migrations.AddIndex(
            model_name="company",
            index=models.Index(fields=["workspace", "name"], name="companies_c_workspa_8ea58a_idx"),
        ),
        migrations.AddConstraint(
            model_name="company",
            constraint=models.UniqueConstraint(
                condition=models.Q(("domain__gt", "")),
                fields=("workspace", "domain"),
                name="unique_workspace_company_domain",
            ),
        ),
    ]
