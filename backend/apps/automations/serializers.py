"""DRF serializers for the automations API (M8).

- `AutomationSerializer` exposes the draft graph as writable so the editor
  can autosave.
- `AutomationVersionSerializer` is read-only; versions are immutable.
- `AutomationRunSerializer` is read-only and inlines step runs in detail
  responses to power the run-inspector UI.
"""

from __future__ import annotations

from rest_framework import serializers

from .models import (
    Automation,
    AutomationRun,
    AutomationStepRun,
    AutomationVersion,
)


class AutomationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Automation
        fields = (
            "id",
            "name",
            "description",
            "status",
            "trigger",
            "graph",
            "version",
            "published_version",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "version",
            "published_version",
            "created_by",
            "created_at",
            "updated_at",
        )


class AutomationVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutomationVersion
        fields = (
            "id",
            "automation",
            "version_number",
            "graph",
            "trigger",
            "published_by",
            "published_at",
        )
        read_only_fields = fields


class AutomationStepRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutomationStepRun
        fields = (
            "id",
            "step_id",
            "attempt",
            "status",
            "started_at",
            "finished_at",
            "input",
            "output",
            "model",
            "cost_cents",
            "error",
            "idempotency_key",
        )
        read_only_fields = fields


class AutomationRunSerializer(serializers.ModelSerializer):
    """List representation — flat fields only, no step runs."""

    class Meta:
        model = AutomationRun
        fields = (
            "id",
            "automation",
            "version",
            "status",
            "current_step_id",
            "trigger_payload",
            "resume_at",
            "started_at",
            "finished_at",
            "attempt",
        )
        read_only_fields = fields


class AutomationRunDetailSerializer(AutomationRunSerializer):
    """Detail representation — includes step_runs for the inspector."""

    step_runs = AutomationStepRunSerializer(many=True, read_only=True)
    state_snapshot = serializers.JSONField(read_only=True)

    class Meta(AutomationRunSerializer.Meta):
        fields = AutomationRunSerializer.Meta.fields + ("state_snapshot", "step_runs")
        read_only_fields = fields


class StartRunSerializer(serializers.Serializer):
    """Request body for `POST /automations/{id}/start_run/`."""

    trigger_payload = serializers.JSONField(required=False, default=dict)
