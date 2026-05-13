"""ViewSets for the automations editor + run inspector (M8) + public
webhook firing endpoint (M9.S1)."""

from __future__ import annotations

import hashlib
import hmac
import json

from django.db.models import F
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.workspaces.permissions import IsWorkspaceManager, IsWorkspaceMember

from .exceptions import GraphError
from .models import (
    Automation,
    AutomationRun,
    AutomationVersion,
    FormEndpoint,
    WebhookEndpoint,
)
from .serializers import (
    AutomationRunDetailSerializer,
    AutomationRunSerializer,
    AutomationSerializer,
    AutomationVersionSerializer,
    StartRunSerializer,
)
from .tasks import cancel_run as cancel_run_service
from .tasks import kick_off, publish_automation
from .triggers import run_automation_with_payload

from apps.ai.exceptions import AIClientError, AIResponseError
from apps.ai.services import generate_automation_graph


class AutomationViewSet(viewsets.ModelViewSet):
    serializer_class = AutomationSerializer
    permission_classes = [IsWorkspaceMember]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_permissions(self):  # type: ignore[no-untyped-def]
        if self.action in {
            "create",
            "update",
            "partial_update",
            "destroy",
            "publish",
            "start_run",
            "generate_from_nl",
        }:
            return [IsWorkspaceManager()]
        return [IsWorkspaceMember()]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        workspace_id = getattr(self.request, "workspace_id", None)
        if not workspace_id:
            return Automation.objects.none()
        return (
            Automation.objects.for_workspace(workspace_id)
            .select_related("created_by", "published_version")
            .order_by("-created_at")
        )

    def perform_create(self, serializer):  # type: ignore[no-untyped-def]
        workspace_id = getattr(self.request, "workspace_id", None)
        serializer.save(workspace_id=workspace_id, created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):  # type: ignore[no-untyped-def]
        automation = self.get_object()
        try:
            version = publish_automation(automation, request.user)
        except GraphError as exc:
            raise ValidationError({"graph": str(exc)}) from exc
        return Response(
            AutomationVersionSerializer(version).data, status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["get"])
    def versions(self, request, pk=None):  # type: ignore[no-untyped-def]
        automation = self.get_object()
        qs = automation.versions.all().order_by("-version_number")
        page = self.paginate_queryset(qs)
        serializer = AutomationVersionSerializer(page or qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="generate_from_nl")
    def generate_from_nl(self, request, pk=None):  # type: ignore[no-untyped-def]
        """Run the `automations.author_from_nl.v1` Claude prompt and return a
        proposed graph WITHOUT saving. The frontend reviews + commits via PATCH.
        """
        automation = self.get_object()
        description = (request.data.get("description") or "").strip()
        if not description:
            raise ValidationError({"description": "required"})
        workspace_context = (request.data.get("workspace_context") or "").strip()
        try:
            graph, response = generate_automation_graph(
                workspace=automation.workspace,
                description=description,
                requested_by=request.user,
                workspace_context=workspace_context,
            )
        except AIResponseError as exc:
            raise ValidationError({"graph": str(exc)}) from exc
        except AIClientError as exc:
            return Response(
                {"detail": f"AI provider error: {exc}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(
            {
                "graph": graph,
                "model": response.model,
                "tokens_in": response.tokens_in,
                "tokens_out": response.tokens_out,
                "latency_ms": response.latency_ms,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="start_run")
    def start_run(self, request, pk=None):  # type: ignore[no-untyped-def]
        """Manual trigger — kicks off a run using the published version."""
        automation = self.get_object()
        if automation.published_version_id is None:
            raise ValidationError(
                {"detail": "automation has no published version — publish before running"}
            )
        serializer = StartRunSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        run = AutomationRun.objects.create(
            automation=automation,
            workspace=automation.workspace,
            version_id=automation.published_version_id,
            trigger_payload=serializer.validated_data.get("trigger_payload") or {},
        )
        kick_off(run)
        run.refresh_from_db()
        return Response(
            AutomationRunDetailSerializer(run).data, status=status.HTTP_201_CREATED
        )


class AutomationRunViewSet(viewsets.ReadOnlyModelViewSet):
    """Run inspector backend: list / detail + cancel action."""

    permission_classes = [IsWorkspaceMember]

    def get_permissions(self):  # type: ignore[no-untyped-def]
        if self.action == "cancel":
            return [IsWorkspaceManager()]
        return [IsWorkspaceMember()]

    def get_serializer_class(self):  # type: ignore[no-untyped-def]
        if self.action == "list":
            return AutomationRunSerializer
        return AutomationRunDetailSerializer

    def get_queryset(self):  # type: ignore[no-untyped-def]
        workspace_id = getattr(self.request, "workspace_id", None)
        if not workspace_id:
            return AutomationRun.objects.none()
        qs = (
            AutomationRun.objects.for_workspace(workspace_id)
            .select_related("automation", "version")
            .prefetch_related("step_runs")
        )
        automation_id = self.request.query_params.get("automation")
        if automation_id:
            qs = qs.filter(automation_id=automation_id)
        run_status = self.request.query_params.get("status")
        if run_status:
            qs = qs.filter(status=run_status)
        return qs

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):  # type: ignore[no-untyped-def]
        run = self.get_object()
        result = cancel_run_service(run)
        run.refresh_from_db()
        return Response(
            {**AutomationRunDetailSerializer(run).data, "cancelled": result == "cancelled"}
        )


class WebhookFireView(APIView):
    """Public, unauthenticated `POST /api/webhooks/{token}/`.

    Verifies HMAC-SHA256 of the raw request body against the endpoint's
    secret, then kicks off the bound automation. The signature header
    accepts either `sha256=<hex>` (GitHub-style) or a bare hex digest.
    Returns 200 + `{run_id}` on success.
    """

    authentication_classes: list = []
    permission_classes = [AllowAny]

    SIGNATURE_HEADER = "HTTP_X_OFFSIDE_SIGNATURE"

    def post(self, request, token: str):  # type: ignore[no-untyped-def]
        try:
            endpoint = WebhookEndpoint.objects.select_related("automation").get(token=token)
        except WebhookEndpoint.DoesNotExist:
            return Response({"detail": "unknown token"}, status=status.HTTP_404_NOT_FOUND)

        if not endpoint.is_active:
            return Response({"detail": "endpoint disabled"}, status=status.HTTP_403_FORBIDDEN)

        raw_body: bytes = request.body or b""
        provided = request.META.get(self.SIGNATURE_HEADER, "")
        if not _verify_signature(secret=endpoint.secret, body=raw_body, provided=provided):
            return Response(
                {"detail": "invalid signature"}, status=status.HTTP_401_UNAUTHORIZED
            )

        # Parse the body as JSON if it's not already (DRF won't have done this
        # for us when we read .body directly). Bare bytes / non-JSON payloads
        # still fire the run with `{}`.
        payload: dict
        try:
            parsed = json.loads(raw_body.decode("utf-8") or "null")
            payload = parsed if isinstance(parsed, dict) else {"body": parsed}
        except (ValueError, UnicodeDecodeError):
            payload = {"raw": raw_body[:1024].decode("utf-8", errors="replace")}

        run_id = run_automation_with_payload(
            endpoint.automation,
            trigger_type="webhook",
            payload={**payload, "webhook_token": endpoint.token},
        )
        if run_id is None:
            return Response(
                {"detail": "automation is not active or has no published version"},
                status=status.HTTP_409_CONFLICT,
            )

        # Audit counters. Update last-fired_at + fire_count atomically.
        WebhookEndpoint.objects.filter(pk=endpoint.pk).update(
            last_fired_at=timezone.now(),
            fire_count=F("fire_count") + 1,
        )

        return Response({"run_id": run_id}, status=status.HTTP_200_OK)


class FormSubmitView(APIView):
    """Public, unauthenticated `POST /api/forms/{token}/submit/`.

    No HMAC. Rate-limited per endpoint via a min-gap between
    `last_submission_at` and `now` derived from
    `rate_limit_per_minute`. Body becomes the run's trigger_payload.
    """

    authentication_classes: list = []
    permission_classes = [AllowAny]

    def post(self, request, token: str):  # type: ignore[no-untyped-def]
        try:
            endpoint = FormEndpoint.objects.select_related("automation").get(token=token)
        except FormEndpoint.DoesNotExist:
            return Response({"detail": "unknown token"}, status=status.HTTP_404_NOT_FOUND)

        if not endpoint.is_active:
            return Response({"detail": "form disabled"}, status=status.HTTP_403_FORBIDDEN)

        # Rate limit: min gap = 60 / rate_limit_per_minute seconds.
        if endpoint.last_submission_at and endpoint.rate_limit_per_minute > 0:
            min_gap = 60.0 / endpoint.rate_limit_per_minute
            elapsed = (timezone.now() - endpoint.last_submission_at).total_seconds()
            if elapsed < min_gap:
                retry_after = max(1, int(round(min_gap - elapsed)))
                return Response(
                    {"detail": "rate limited", "retry_after_seconds": retry_after},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                    headers={"Retry-After": str(retry_after)},
                )

        # Body parsing — JSON preferred, form-encoded falls back to request.data.
        raw_body: bytes = request.body or b""
        payload: dict
        try:
            parsed = json.loads(raw_body.decode("utf-8") or "null")
            if isinstance(parsed, dict):
                payload = parsed
            elif parsed is None:
                payload = {}
            else:
                payload = {"body": parsed}
        except (ValueError, UnicodeDecodeError):
            # Likely form-encoded — DRF's parser already populated request.data.
            try:
                payload = {k: v for k, v in request.data.items()}
            except Exception:  # noqa: BLE001 — opaque bodies still fire
                payload = {"raw": raw_body[:1024].decode("utf-8", errors="replace")}

        run_id = run_automation_with_payload(
            endpoint.automation,
            trigger_type="form",
            payload={**payload, "form_token": endpoint.token},
        )
        if run_id is None:
            return Response(
                {"detail": "automation is not active or has no published version"},
                status=status.HTTP_409_CONFLICT,
            )

        FormEndpoint.objects.filter(pk=endpoint.pk).update(
            last_submission_at=timezone.now(),
            submission_count=F("submission_count") + 1,
        )
        return Response({"run_id": run_id}, status=status.HTTP_200_OK)


def _verify_signature(*, secret: str, body: bytes, provided: str) -> bool:
    if not provided or not secret:
        return False
    if provided.startswith("sha256="):
        provided = provided[len("sha256=") :]
    expected = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, provided.strip())


class AutomationVersionViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only listing of every published version across an automation.

    Mostly redundant with the nested `/automations/{id}/versions/` action,
    but exposed flat for convenience (e.g. linking from a run inspector page
    straight to the version definition that produced it).
    """

    serializer_class = AutomationVersionSerializer
    permission_classes = [IsWorkspaceMember]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        workspace_id = getattr(self.request, "workspace_id", None)
        if not workspace_id:
            return AutomationVersion.objects.none()
        return AutomationVersion.objects.for_workspace(workspace_id).select_related(
            "automation", "published_by"
        )
