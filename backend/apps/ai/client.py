"""Thin Anthropic wrapper that writes an `AICall` telemetry row per call.

Tests replace `_get_anthropic()` via dependency injection (see `services.py`'s
`generate_automation_graph` for the public surface and tests for the override
pattern) so they never hit the real API. Production reads
`ANTHROPIC_API_KEY` from the environment.

Cost model (in cents): Sonnet 4.6 list pricing as of 2026-05. Bumped per
M11's full multi-provider abstraction; for M8 we hard-code Sonnet costs
so the telemetry rows aren't all zero.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from typing import Any

from django.utils import timezone

from .exceptions import AIClientError
from .models import AICall, AICallStatus
from .prompts import Prompt

log = logging.getLogger("apps.ai")


# Cents per million tokens. Bump when pricing changes.
_PRICING_PER_MTOK_CENTS: dict[str, tuple[int, int]] = {
    # model: (input cents/Mtok, output cents/Mtok)
    "claude-sonnet-4-6": (300, 1500),
    "claude-opus-4-7": (1500, 7500),
    "claude-haiku-4-5-20251001": (80, 400),
}


def _cost_cents(model: str, tokens_in: int, tokens_out: int) -> int:
    pricing = _PRICING_PER_MTOK_CENTS.get(model)
    if not pricing:
        return 0
    in_cents = (tokens_in * pricing[0]) // 1_000_000
    out_cents = (tokens_out * pricing[1]) // 1_000_000
    return int(in_cents + out_cents)


@dataclass
class AIResponse:
    parsed_tool_input: dict[str, Any] | None
    raw_text: str
    model: str
    tokens_in: int
    tokens_out: int
    latency_ms: int


def _get_anthropic_factory():  # pragma: no cover — overridden in tests
    """Return the anthropic.Anthropic() client. Wrapped so tests can swap."""
    import anthropic  # imported lazily so apps/ai can be loaded without the SDK

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise AIClientError("ANTHROPIC_API_KEY not configured")
    return anthropic.Anthropic(api_key=api_key)


# Test-time override. Production keeps this None and the factory is used.
_override_caller = None  # type: ignore[var-annotated]


def set_override_caller(fn) -> None:  # type: ignore[no-untyped-def]
    """For tests: pass a function `(prompt, kwargs) -> AIResponse` to avoid real API hits."""
    global _override_caller
    _override_caller = fn


def call(
    *,
    prompt: Prompt,
    workspace,  # apps.workspaces.models.Workspace — avoiding import for typing
    requested_by=None,
    metadata: dict[str, Any] | None = None,
    **build_kwargs: Any,
):  # type: ignore[no-untyped-def]
    """Run a registered prompt, persist a telemetry row, return AIResponse.

    Raises AIClientError on transport / parsing failure. The telemetry row
    is written either way (status=ERROR on failure) so cost accounting
    never silently drops a call.
    """
    request_kwargs = prompt.build(**build_kwargs)
    started = time.monotonic()

    try:
        if _override_caller is not None:
            response = _override_caller(prompt, request_kwargs)
        else:
            response = _real_call(prompt=prompt, request_kwargs=request_kwargs)
    except AIClientError:
        raise
    except Exception as exc:  # noqa: BLE001 — surface all transport errors
        latency_ms = int((time.monotonic() - started) * 1000)
        AICall.objects.create(
            workspace=workspace,
            requested_by=requested_by,
            prompt_name=prompt.name,
            model=prompt.model,
            status=AICallStatus.ERROR,
            tokens_in=0,
            tokens_out=0,
            cost_cents=0,
            latency_ms=latency_ms,
            error=str(exc)[:4096],
            metadata=metadata or {},
        )
        log.exception("AI call failed: %s", prompt.name)
        raise AIClientError(str(exc)) from exc

    AICall.objects.create(
        workspace=workspace,
        requested_by=requested_by,
        prompt_name=prompt.name,
        model=response.model,
        status=AICallStatus.SUCCESS,
        tokens_in=response.tokens_in,
        tokens_out=response.tokens_out,
        cost_cents=_cost_cents(response.model, response.tokens_in, response.tokens_out),
        latency_ms=response.latency_ms,
        metadata=metadata or {},
    )
    return response


def _real_call(*, prompt: Prompt, request_kwargs: dict[str, Any]) -> AIResponse:
    client = _get_anthropic_factory()
    started = time.monotonic()
    msg = client.messages.create(model=prompt.model, **request_kwargs)
    latency_ms = int((time.monotonic() - started) * 1000)

    tool_input: dict[str, Any] | None = None
    raw_text = ""
    for block in msg.content:
        btype = getattr(block, "type", None)
        if btype == "tool_use":
            tool_input = dict(getattr(block, "input", {}))
        elif btype == "text":
            raw_text += getattr(block, "text", "")

    usage = getattr(msg, "usage", None)
    tokens_in = getattr(usage, "input_tokens", 0) if usage else 0
    tokens_out = getattr(usage, "output_tokens", 0) if usage else 0

    return AIResponse(
        parsed_tool_input=tool_input,
        raw_text=raw_text,
        model=getattr(msg, "model", prompt.model),
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        latency_ms=latency_ms,
    )


__all__ = ["AIResponse", "call", "set_override_caller"]
