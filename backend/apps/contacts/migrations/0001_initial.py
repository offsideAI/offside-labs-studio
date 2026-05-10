"""Initial migration for Contact. Hand-authored.

Depends on companies/0001 because Contact has an FK to Company.
"""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import apps.workspaces.managers


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("workspaces", "0001_initial"),
        ("companies", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Contact",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("first_name", models.CharField(blank=True, max_length=100)),
                ("last_name", models.CharField(blank=True, max_length=100)),
                ("primary_email", models.EmailField(blank=True, db_index=True, max_length=254)),
                ("phones", models.JSONField(blank=True, default=list)),
                ("title", models.CharField(blank=True, max_length=200)),
                (
                    "lifecycle_stage",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("lead", "Lead"),
                            ("qualified", "Qualified"),
                            ("customer", "Customer"),
                            ("churned", "Churned"),
                        ],
                        max_length=16,
                    ),
                ),
                ("source", models.CharField(blank=True, max_length=100)),
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
                        related_name="contacts",
                        to="companies.company",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="contacts_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="owned_contacts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "workspace",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="contacts",
                        to="workspaces.workspace",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
            managers=[("objects", apps.workspaces.managers.WorkspaceScopedManager())],
        ),
        migrations.AddIndex(
            model_name="contact",
            index=models.Index(
                fields=["workspace", "primary_email"],
                name="contacts_co_workspa_4b8c2d_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="contact",
            index=models.Index(
                fields=["workspace", "last_name", "first_name"],
                name="contacts_co_workspa_5c9d3e_idx",
            ),
        ),
    ]
