"""Filter DSL evaluator. Shared across contacts/companies/deals (M4–M5+).

Schema:
  {"and": [<filter>, ...]}
  {"or":  [<filter>, ...]}
  {"not": <filter>}
  {"field": "name", "op": "eq", "value": "foo"}

Operators: eq, neq, contains, icontains, gt, gte, lt, lte, in, is_null
Field paths: dotted for JSONB lookups — "custom.lead_score" → custom__lead_score.
Only fields in `allowed_fields` (and "custom" for arbitrary custom-field keys) are accepted;
any other field raises ValueError to keep the surface auditable.
"""

from __future__ import annotations

import json
from typing import Any

from django.db.models import Q


_OP_TO_LOOKUP = {
    "eq": "exact",
    "neq": "exact",
    "contains": "contains",
    "icontains": "icontains",
    "gt": "gt",
    "gte": "gte",
    "lt": "lt",
    "lte": "lte",
    "in": "in",
    "is_null": "isnull",
}


def evaluate_filter_dsl(node: Any, allowed_fields: set[str]) -> Q:
    """Evaluate a parsed JSON filter node into a Django Q.

    Raises ValueError for any malformed input.
    """
    if not isinstance(node, dict):
        raise ValueError("filter node must be an object")

    if "and" in node:
        children = node["and"]
        if not isinstance(children, list):
            raise ValueError("`and` must be a list")
        q = Q()
        for child in children:
            q &= evaluate_filter_dsl(child, allowed_fields)
        return q

    if "or" in node:
        children = node["or"]
        if not isinstance(children, list) or not children:
            raise ValueError("`or` must be a non-empty list")
        q = evaluate_filter_dsl(children[0], allowed_fields)
        for child in children[1:]:
            q |= evaluate_filter_dsl(child, allowed_fields)
        return q

    if "not" in node:
        return ~evaluate_filter_dsl(node["not"], allowed_fields)

    if "field" in node and "op" in node:
        field = node["field"]
        op = node["op"]
        value = node.get("value")

        if not isinstance(field, str) or not isinstance(op, str):
            raise ValueError("`field` and `op` must be strings")
        if op not in _OP_TO_LOOKUP:
            raise ValueError(f"unknown operator: {op}")

        head = field.split(".", 1)[0]
        if head not in allowed_fields:
            raise ValueError(f"field not allowed: {field}")

        django_field = field.replace(".", "__")
        lookup = _OP_TO_LOOKUP[op]
        kwargs = {f"{django_field}__{lookup}": value}
        q = Q(**kwargs)
        return ~q if op == "neq" else q

    raise ValueError(f"invalid filter node: {node}")


def apply_filter_dsl(queryset, request, allowed_fields: set[str]):  # type: ignore[no-untyped-def]
    """Read ?filter=<urlencoded JSON> from the request and apply it to the queryset.

    Returns the queryset unchanged when no filter is present. On parse error the
    view should surface a 400 — we re-raise ValueError for the caller to translate.
    """
    raw = request.query_params.get("filter") if hasattr(request, "query_params") else None
    if not raw:
        return queryset
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"filter is not valid JSON: {exc}") from exc
    q = evaluate_filter_dsl(parsed, allowed_fields)
    return queryset.filter(q)
