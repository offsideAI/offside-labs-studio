"""Prompt registry. One module per prompt; this file is the index.

Conventions:
- Names follow `<domain>.<intent>.<version>` (e.g. `automations.author_from_nl.v1`).
- Each registered prompt declares its default model and a builder that
  returns the SDK request kwargs (`system`, `messages`, `tools?`).
- Versioning is explicit: bump the suffix when you change the system
  prompt or tool schema. Old versions stay registered so retro-querying
  telemetry by prompt_name still works.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable

from apps.automations.actions import all_names as automation_action_names


# Default model for editor-time calls. Run-time AI actions can override
# per call. The full provider-fallback chain (Claude → OpenAI → Gemini)
# lands in M11.
DEFAULT_MODEL = "claude-sonnet-4-6"


@dataclass(frozen=True)
class Prompt:
    name: str
    model: str
    build: Callable[..., dict[str, Any]]


_REGISTRY: dict[str, Prompt] = {}


def register(prompt: Prompt) -> Prompt:
    _REGISTRY[prompt.name] = prompt
    return prompt


def get(name: str) -> Prompt:
    if name not in _REGISTRY:
        raise KeyError(f"unknown prompt {name!r}; registered: {sorted(_REGISTRY)}")
    return _REGISTRY[name]


# --- automations.author_from_nl.v1 ---------------------------------------------

_GRAPH_TOOL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "start_node_id": {
            "type": "string",
            "description": "ID of the first node to execute.",
        },
        "nodes": {
            "type": "object",
            "description": (
                "Map of node_id → node. Every node has `type` and (except "
                "`end`) one or more outgoing edge fields. Available types: "
                "action, delay, approval, branch, wait_for_event, end."
            ),
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": [
                            "action",
                            "delay",
                            "approval",
                            "branch",
                            "wait_for_event",
                            "end",
                        ],
                    },
                    "label": {"type": "string"},
                    "config": {
                        "type": "object",
                        "description": (
                            "Per-type config. action: {action, input}. "
                            "delay: {seconds}. approval: {summary, ttl_seconds?}. "
                            "branch: {field, op, value}. wait_for_event: {event_key}."
                        ),
                    },
                    "next": {"type": "string"},
                    "approve_next": {"type": "string"},
                    "reject_next": {"type": "string"},
                    "true_next": {"type": "string"},
                    "false_next": {"type": "string"},
                },
                "required": ["type"],
            },
        },
    },
    "required": ["start_node_id", "nodes"],
}


def _author_from_nl_system_prompt(*, action_names: list[str]) -> str:
    return (
        "You are a workflow architect for the Offside CRM. The user describes "
        "a workflow in plain English and you return a node-graph definition.\n\n"
        "Graph schema:\n"
        "- start_node_id (string): id of the first node.\n"
        "- nodes (object): map of node_id → node.\n"
        "  - type: one of action | delay | approval | branch | wait_for_event | end\n"
        "  - label: short human label.\n"
        "  - config: per-type config (see below).\n"
        "  - next / approve_next / reject_next / true_next / false_next: id of the next node.\n\n"
        "Node-type rules:\n"
        "- action.config = {action: <registered action name>, input: <object>}\n"
        "  Available actions: " + ", ".join(action_names) + "\n"
        "- delay.config = {seconds: <int>}\n"
        "- approval.config = {summary: <string>, ttl_seconds?: <int default 604800>}\n"
        "  Approval nodes use `approve_next` + `reject_next` (no `next`).\n"
        "- branch.config = {field: <path>, op: eq|neq|gt|gte|lt|lte|in|is_null, value: <any>}\n"
        "  Branch nodes use `true_next` + `false_next`.\n"
        "- wait_for_event.config = {event_key: <string>}\n"
        "- end nodes have no outgoing edges.\n\n"
        "Templating: action `config.input` values can reference previous step "
        "outputs as `{{ <node_id>.<dotted>.<path> }}` strings.\n\n"
        "Always:\n"
        "1. Use stable ids like n1, n2, … (do NOT reuse ids).\n"
        "2. End every branch with an `end` node.\n"
        "3. Prefer the fewest nodes that accomplish the request.\n"
        "4. Return ONLY a tool call to build_graph — no prose."
    )


def _author_from_nl_build(
    *,
    description: str,
    workspace_context: str = "",
) -> dict[str, Any]:
    system = _author_from_nl_system_prompt(action_names=sorted(automation_action_names()))
    user_content = description.strip()
    if workspace_context:
        user_content = (
            "Workspace context (for reference — entities, custom fields, pipelines):\n"
            + workspace_context.strip()
            + "\n\nUser request:\n"
            + user_content
        )
    return {
        "system": system,
        "messages": [{"role": "user", "content": user_content}],
        "tools": [
            {
                "name": "build_graph",
                "description": "Return the node graph that satisfies the user's request.",
                "input_schema": _GRAPH_TOOL_SCHEMA,
            }
        ],
        "tool_choice": {"type": "tool", "name": "build_graph"},
        "max_tokens": 2048,
    }


AUTHOR_FROM_NL_V1 = register(
    Prompt(
        name="automations.author_from_nl.v1",
        model=DEFAULT_MODEL,
        build=_author_from_nl_build,
    )
)


# Helper exposed for tests / introspection.
def author_from_nl_tool_schema() -> dict[str, Any]:
    return json.loads(json.dumps(_GRAPH_TOOL_SCHEMA))
