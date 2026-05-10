"""Graph schema + helpers.

Schema (v1):

    {
      "start_node_id": "n1",
      "nodes": {
        "n1": {"type": "action", "config": {"action": "noop", "input": {...}}, "next": "n2"},
        "n2": {"type": "delay", "config": {"seconds": 60}, "next": "n3"},
        "n3": {"type": "approval", "config": {"summary": "..."}, "approve_next": "n4", "reject_next": "end"},
        "n4": {"type": "branch", "config": {"field": "n1.ok", "op": "eq", "value": true},
               "true_next": "n5", "false_next": "end"},
        "n5": {"type": "wait_for_event", "config": {"event_key": "..."}, "next": "n6"},
        "end": {"type": "end"}
      }
    }

Templates: action `input` values may be either literals or
`{{ <node_id>.<path>.<to>.<field> }}` strings that get resolved against
the run's `state_snapshot` at execution time.
"""

from __future__ import annotations

from typing import Any

from .exceptions import GraphError

NODE_TYPES = ("action", "delay", "approval", "branch", "wait_for_event", "end")


def get_node(graph: dict[str, Any], node_id: str) -> dict[str, Any]:
    nodes = graph.get("nodes") or {}
    if node_id not in nodes:
        raise GraphError(f"unknown node: {node_id!r}")
    return nodes[node_id]


def start_node_id(graph: dict[str, Any]) -> str:
    node_id = graph.get("start_node_id")
    if not node_id:
        raise GraphError("graph missing start_node_id")
    if "nodes" not in graph or node_id not in graph["nodes"]:
        raise GraphError(f"start_node_id {node_id!r} not in nodes")
    return node_id


def validate(graph: dict[str, Any]) -> None:
    """Light schema check; full validation lands with the editor in M8."""
    if not isinstance(graph, dict):
        raise GraphError("graph must be an object")
    if not isinstance(graph.get("nodes"), dict):
        raise GraphError("graph.nodes must be an object")
    start_node_id(graph)
    for node_id, node in graph["nodes"].items():
        if not isinstance(node, dict):
            raise GraphError(f"node {node_id!r} must be an object")
        if node.get("type") not in NODE_TYPES:
            raise GraphError(f"node {node_id!r} has unknown type {node.get('type')!r}")


def resolve_template(value: Any, state: dict[str, Any]) -> Any:
    """Resolve `{{ a.b.c }}` references against the run state. Returns
    other values unchanged."""
    if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
        path = value[2:-2].strip()
        return _path_get(state, path)
    if isinstance(value, dict):
        return {k: resolve_template(v, state) for k, v in value.items()}
    if isinstance(value, list):
        return [resolve_template(v, state) for v in value]
    return value


def _path_get(state: dict[str, Any], dotted_path: str) -> Any:
    current: Any = state
    for part in dotted_path.split("."):
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def evaluate_branch(actual: Any, op: str, value: Any) -> bool:
    if op == "eq":
        return actual == value
    if op == "neq":
        return actual != value
    if op == "gt":
        return actual is not None and actual > value
    if op == "gte":
        return actual is not None and actual >= value
    if op == "lt":
        return actual is not None and actual < value
    if op == "lte":
        return actual is not None and actual <= value
    if op == "in":
        return actual in (value or [])
    if op == "is_null":
        return actual is None
    return False
