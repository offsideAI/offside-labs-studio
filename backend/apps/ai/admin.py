"""Django admin — read-only AICall telemetry browser."""

from __future__ import annotations

from django.contrib import admin

from .models import AICall


@admin.register(AICall)
class AICallAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "prompt_name",
        "model",
        "status",
        "tokens_in",
        "tokens_out",
        "cost_cents",
        "latency_ms",
        "workspace",
        "created_at",
    )
    list_filter = ("status", "prompt_name", "model")
    search_fields = ("workspace__slug", "prompt_name", "error")
    readonly_fields = (
        "workspace",
        "requested_by",
        "prompt_name",
        "model",
        "status",
        "tokens_in",
        "tokens_out",
        "cost_cents",
        "latency_ms",
        "run",
        "step_id",
        "error",
        "metadata",
        "created_at",
    )
    autocomplete_fields = ("workspace", "requested_by", "run")
