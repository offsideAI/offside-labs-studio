"""Health check endpoints. Public — used by DO App Platform probes and the docker-compose healthcheck."""

from __future__ import annotations

import os

from django.db import connection
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


@api_view(["GET"])
@permission_classes([AllowAny])
def live(request) -> JsonResponse:  # type: ignore[no-untyped-def]
    """Liveness probe — is the process responsive?"""
    return JsonResponse({"status": "ok"})


@api_view(["GET"])
@permission_classes([AllowAny])
def ready(request) -> JsonResponse:  # type: ignore[no-untyped-def]
    """Readiness probe — are dependencies (Postgres, Redis) reachable?"""
    checks: dict[str, str] = {}

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        checks["postgres"] = "ok"
    except Exception as exc:  # noqa: BLE001 — surface every failure mode
        checks["postgres"] = f"error: {exc.__class__.__name__}"

    try:
        from redis import Redis

        redis_client = Redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379/0"))
        redis_client.ping()
        checks["redis"] = "ok"
    except Exception as exc:  # noqa: BLE001
        checks["redis"] = f"error: {exc.__class__.__name__}"

    overall_ok = all(value == "ok" for value in checks.values())
    return JsonResponse(
        {"status": "ok" if overall_ok else "degraded", "checks": checks},
        status=200 if overall_ok else 503,
    )
