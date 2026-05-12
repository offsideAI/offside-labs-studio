"""Public service entry points for editor-time AI features (M8.S3).

Run-time AI actions (M11) will register through `apps.automations.actions`
and call `client.call(...)` directly; the helpers here are for surfaces
the user invokes by hand.
"""

from __future__ import annotations

from typing import Any

from apps.automations.graph import validate as validate_graph

from . import client, prompts
from .exceptions import AIResponseError


def generate_automation_graph(
    *,
    workspace,  # apps.workspaces.models.Workspace
    description: str,
    requested_by=None,
    workspace_context: str = "",
):  # type: ignore[no-untyped-def]
    """Call `automations.author_from_nl.v1` and return a validated graph.

    Persists an `AICall` telemetry row (success or error) via the client
    wrapper. Raises AIResponseError if the model returns no tool call or
    the returned shape fails `graph.validate`.
    """
    prompt = prompts.get("automations.author_from_nl.v1")
    response = client.call(
        prompt=prompt,
        workspace=workspace,
        requested_by=requested_by,
        metadata={"description_chars": len(description or "")},
        description=description,
        workspace_context=workspace_context,
    )

    tool_input = response.parsed_tool_input
    if not tool_input:
        raise AIResponseError("model returned no graph tool call")

    graph = _coerce_graph(tool_input)
    try:
        validate_graph(graph)
    except Exception as exc:  # GraphError or anything else from validate
        raise AIResponseError(f"generated graph failed validation: {exc}") from exc

    return graph, response


def _coerce_graph(raw: dict[str, Any]) -> dict[str, Any]:
    """Light shape pass — fill missing `config` defaults and ensure strings."""
    out: dict[str, Any] = {
        "start_node_id": str(raw.get("start_node_id") or ""),
        "nodes": {},
    }
    src_nodes = raw.get("nodes") or {}
    if not isinstance(src_nodes, dict):
        raise AIResponseError("nodes must be an object")

    for node_id, node in src_nodes.items():
        if not isinstance(node, dict):
            raise AIResponseError(f"node {node_id!r} must be an object")
        config = node.get("config")
        if config is None:
            config = {}
        elif not isinstance(config, dict):
            raise AIResponseError(f"node {node_id!r} config must be an object")
        out["nodes"][str(node_id)] = {
            "type": node.get("type"),
            "label": str(node.get("label", "")) if node.get("label") else "",
            "config": config,
            **({"next": str(node["next"])} if node.get("next") else {}),
            **({"approve_next": str(node["approve_next"])} if node.get("approve_next") else {}),
            **({"reject_next": str(node["reject_next"])} if node.get("reject_next") else {}),
            **({"true_next": str(node["true_next"])} if node.get("true_next") else {}),
            **({"false_next": str(node["false_next"])} if node.get("false_next") else {}),
        }
    return out


__all__ = ["generate_automation_graph"]
