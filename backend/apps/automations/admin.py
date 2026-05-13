"""Django admin — minimal Run Inspector view for M7.

Lists runs with status + step counts; the detail page surfaces step
input/output/error/idempotency_key so engineers can debug crashes
without writing SQL.
"""

from __future__ import annotations

from django.contrib import admin

from .models import (
    AgentPolicy,
    Automation,
    AutomationRun,
    AutomationStepRun,
    AutomationVersion,
    HitlRequest,
    WebhookEndpoint,
)


@admin.register(Automation)
class AutomationAdmin(admin.ModelAdmin):
    list_display = ("name", "version", "status", "workspace", "created_by", "created_at")
    list_filter = ("status",)
    search_fields = ("name", "workspace__slug")
    autocomplete_fields = ("workspace", "created_by", "published_version")
    readonly_fields = ("created_at", "updated_at")


@admin.register(AutomationVersion)
class AutomationVersionAdmin(admin.ModelAdmin):
    list_display = ("automation", "version_number", "published_by", "published_at")
    search_fields = ("automation__name",)
    readonly_fields = (
        "automation",
        "workspace",
        "version_number",
        "graph",
        "trigger",
        "published_by",
        "published_at",
    )
    autocomplete_fields = ("automation", "workspace", "published_by")


class AutomationStepRunInline(admin.TabularInline):
    model = AutomationStepRun
    extra = 0
    can_delete = False
    fields = (
        "step_id",
        "attempt",
        "status",
        "started_at",
        "finished_at",
        "cost_cents",
        "idempotency_key",
    )
    readonly_fields = fields
    show_change_link = True


@admin.register(AutomationRun)
class AutomationRunAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "automation",
        "workspace",
        "status",
        "current_step_id",
        "resume_at",
        "started_at",
        "finished_at",
    )
    list_filter = ("status",)
    search_fields = ("automation__name", "workspace__slug", "advancer_task_id")
    readonly_fields = (
        "automation",
        "workspace",
        "trigger_payload",
        "state_snapshot",
        "advancer_task_id",
        "started_at",
        "finished_at",
    )
    inlines = (AutomationStepRunInline,)
    autocomplete_fields = ("automation", "workspace")


@admin.register(AutomationStepRun)
class AutomationStepRunAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "run",
        "step_id",
        "attempt",
        "status",
        "model",
        "cost_cents",
        "started_at",
        "finished_at",
    )
    list_filter = ("status",)
    search_fields = ("step_id", "idempotency_key")
    readonly_fields = (
        "run",
        "step_id",
        "attempt",
        "input",
        "output",
        "error",
        "idempotency_key",
        "started_at",
        "finished_at",
    )


@admin.register(HitlRequest)
class HitlRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "run",
        "step_id",
        "decision",
        "decided_by",
        "decided_at",
        "expires_at",
    )
    list_filter = ("decision",)
    search_fields = ("step_id", "summary")
    readonly_fields = ("token", "created_at")
    autocomplete_fields = ("run", "decided_by")


@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    list_display = (
        "token",
        "label",
        "automation",
        "workspace",
        "is_active",
        "fire_count",
        "last_fired_at",
        "created_by",
        "created_at",
    )
    list_filter = ("is_active",)
    search_fields = ("token", "label", "workspace__slug", "automation__name")
    readonly_fields = ("token", "secret", "fire_count", "last_fired_at", "created_at")
    autocomplete_fields = ("workspace", "automation", "created_by")


@admin.register(AgentPolicy)
class AgentPolicyAdmin(admin.ModelAdmin):
    list_display = ("workspace", "action_type", "mode")
    list_filter = ("mode",)
    search_fields = ("workspace__slug", "action_type")
    autocomplete_fields = ("workspace",)
