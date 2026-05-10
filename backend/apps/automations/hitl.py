"""HITL approval token utilities.

We sign with Django's SECRET_KEY using PyJWT (already a dep through
djangorestframework-simplejwt). Tokens carry `(hitl_id, run_id, exp)`
and a `purpose` claim so they can't be confused with any other JWT.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import jwt
from django.conf import settings
from django.utils import timezone

from .exceptions import HitlTokenError

HITL_TOKEN_PURPOSE = "hitl-approval"
DEFAULT_TTL = timedelta(days=7)


def make_token(*, hitl_id: int, run_id: int, ttl: timedelta = DEFAULT_TTL) -> str:
    payload: dict[str, Any] = {
        "purpose": HITL_TOKEN_PURPOSE,
        "hitl_id": hitl_id,
        "run_id": run_id,
        "exp": int((timezone.now() + ttl).timestamp()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def verify_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError as exc:
        raise HitlTokenError("approval token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise HitlTokenError(f"invalid approval token: {exc}") from exc
    if payload.get("purpose") != HITL_TOKEN_PURPOSE:
        raise HitlTokenError("token purpose mismatch")
    return payload
