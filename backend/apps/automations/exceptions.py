"""Exceptions raised by the workflow runtime."""

from __future__ import annotations


class WorkflowError(Exception):
    """Base class for runtime errors. Step runs catch this and mark the run failed."""


class GraphError(WorkflowError):
    """Malformed graph — missing node, unreachable end, etc."""


class ActionError(WorkflowError):
    """Action handler raised, or the action_name was unknown."""


class HitlTokenError(WorkflowError):
    """Approval token failed validation (expired, malformed, wrong purpose)."""
