"""Action handler registry.

Handlers are pure side-effecting functions: `(workspace, input) -> output`.
The run advancer wraps every call in a per-step idempotency check, so
the handler itself does NOT need to short-circuit on duplicate execution
— the framework does that one layer up via AutomationStepRun.

To register an action:

    @register("crm.move_deal_stage")
    def move_deal_stage(workspace, payload):
        ...
        return {"deal_id": ..., "stage_id": ...}

M9 expands the registry; M11 lands AI-prompt actions.
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from .exceptions import ActionError

ActionHandler = Callable[[Any, dict[str, Any]], dict[str, Any]]

_REGISTRY: dict[str, ActionHandler] = {}

log = logging.getLogger("apps.automations.actions")


def register(name: str) -> Callable[[ActionHandler], ActionHandler]:
    def decorator(fn: ActionHandler) -> ActionHandler:
        if name in _REGISTRY:
            raise ValueError(f"duplicate action: {name}")
        _REGISTRY[name] = fn
        return fn

    return decorator


def get(name: str) -> ActionHandler:
    try:
        return _REGISTRY[name]
    except KeyError as exc:
        raise ActionError(f"unknown action: {name!r}") from exc


def all_names() -> list[str]:
    return sorted(_REGISTRY)


# --- Built-in actions ---


@register("noop")
def action_noop(workspace, payload: dict[str, Any]) -> dict[str, Any]:
    """Returns the payload unchanged. Useful for graph traversal tests."""
    return dict(payload)


@register("log")
def action_log(workspace, payload: dict[str, Any]) -> dict[str, Any]:
    """Logs the payload at info. Returns it for downstream branching."""
    log.info("workflow.log workspace=%s payload=%s", getattr(workspace, "slug", "?"), payload)
    return dict(payload)


@register("crm.create_contact")
def action_create_contact(workspace, payload: dict[str, Any]) -> dict[str, Any]:
    """Creates a Contact in the active workspace. Requires `created_by_id` in payload."""
    from apps.contacts.models import Contact

    if "created_by_id" not in payload:
        raise ActionError("crm.create_contact requires created_by_id")

    contact = Contact.objects.create(
        workspace=workspace,
        first_name=payload.get("first_name", ""),
        last_name=payload.get("last_name", ""),
        primary_email=payload.get("primary_email", ""),
        title=payload.get("title", ""),
        lifecycle_stage=payload.get("lifecycle_stage", ""),
        source=payload.get("source", ""),
        custom=payload.get("custom", {}),
        created_by_id=payload["created_by_id"],
    )
    return {"contact_id": contact.id, "primary_email": contact.primary_email}


@register("crm.move_deal_stage")
def action_move_deal_stage(workspace, payload: dict[str, Any]) -> dict[str, Any]:
    from apps.deals.models import Deal

    if "deal_id" not in payload or "stage_id" not in payload:
        raise ActionError("crm.move_deal_stage requires deal_id and stage_id")

    deal = Deal.objects.get(workspace=workspace, pk=payload["deal_id"])
    deal.stage_id = payload["stage_id"]
    deal.save(update_fields=["stage_id"])
    return {"deal_id": deal.id, "stage_id": deal.stage_id}


# --- M9.S2: HTTP request action ---

_HTTP_ALLOWED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}
_HTTP_DEFAULT_TIMEOUT = 30
_HTTP_MAX_TIMEOUT = 120
_HTTP_RESPONSE_BODY_MAX_BYTES = 256 * 1024  # 256 KB — keep AutomationStepRun.output bounded


@register("crm.http.request")
def action_http_request(workspace, payload: dict[str, Any]) -> dict[str, Any]:
    """Outbound HTTP request from a workflow step.

    Schema:
        url: str — must be http:// or https://
        method: str = "GET" — GET/POST/PUT/PATCH/DELETE/HEAD/OPTIONS
        headers: dict[str, str] = {}
        body: dict | str | None — dict → JSON, str → raw
        auth:
            {type: "none"}                                          # default
            {type: "bearer", token: "..."}                          # Authorization: Bearer …
            {type: "basic", username: "...", password: "..."}       # Authorization: Basic base64
            {type: "header", name: "X-API-Key", value: "..."}       # arbitrary header
        timeout_seconds: int = 30 (max 120)
        expect_json: bool = True — parse response.json() when possible

    Returns:
        {status_code: int, headers: dict, body: <json|str>}

    Idempotency: GET is naturally idempotent. POST/PUT/PATCH/DELETE are
    short-circuited on replay by the M7 framework's idempotency_key on
    AutomationStepRun — handler does NOT need to dedupe itself.
    """
    import base64

    import httpx

    url = payload.get("url")
    if not isinstance(url, str) or not (
        url.startswith("http://") or url.startswith("https://")
    ):
        raise ActionError("crm.http.request requires a URL starting with http:// or https://")

    method = str(payload.get("method") or "GET").upper()
    if method not in _HTTP_ALLOWED_METHODS:
        raise ActionError(f"crm.http.request unsupported method {method!r}")

    timeout = int(payload.get("timeout_seconds") or _HTTP_DEFAULT_TIMEOUT)
    if timeout < 1 or timeout > _HTTP_MAX_TIMEOUT:
        raise ActionError(
            f"timeout_seconds must be between 1 and {_HTTP_MAX_TIMEOUT}, got {timeout}"
        )

    headers: dict[str, str] = {str(k): str(v) for k, v in (payload.get("headers") or {}).items()}

    auth = payload.get("auth") or {"type": "none"}
    auth_type = str(auth.get("type", "none"))
    if auth_type == "bearer":
        token = auth.get("token")
        if not token:
            raise ActionError("bearer auth requires `token`")
        headers["Authorization"] = f"Bearer {token}"
    elif auth_type == "basic":
        user = auth.get("username") or ""
        pw = auth.get("password") or ""
        if not user and not pw:
            raise ActionError("basic auth requires `username` and/or `password`")
        encoded = base64.b64encode(f"{user}:{pw}".encode("utf-8")).decode("ascii")
        headers["Authorization"] = f"Basic {encoded}"
    elif auth_type == "header":
        name = str(auth.get("name") or "")
        value = str(auth.get("value") or "")
        if not name:
            raise ActionError("header auth requires `name`")
        headers[name] = value
    elif auth_type != "none":
        raise ActionError(f"crm.http.request unsupported auth type {auth_type!r}")

    body = payload.get("body")
    json_body = body if isinstance(body, (dict, list)) else None
    content_body = body if isinstance(body, str) else None

    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            response = client.request(
                method=method,
                url=url,
                headers=headers,
                json=json_body,
                content=content_body,
            )
    except httpx.RequestError as exc:
        raise ActionError(f"HTTP request failed: {exc}") from exc

    response_body: Any
    if payload.get("expect_json", True):
        try:
            response_body = response.json()
        except Exception:  # noqa: BLE001 — gracefully fall back to text
            response_body = _truncate_text(response.text)
    else:
        response_body = _truncate_text(response.text)

    return {
        "status_code": response.status_code,
        "headers": dict(response.headers),
        "body": response_body,
    }


def _truncate_text(text: str) -> str:
    encoded = text.encode("utf-8", errors="replace")
    if len(encoded) <= _HTTP_RESPONSE_BODY_MAX_BYTES:
        return text
    return encoded[:_HTTP_RESPONSE_BODY_MAX_BYTES].decode("utf-8", errors="replace") + "…[truncated]"


# --- M9.S2 phase 2: loop action ---

_LOOP_MAX_ITEMS_HARD_CAP = 5000


@register("crm.loop")
def action_loop(workspace, payload: dict[str, Any]) -> dict[str, Any]:
    """Iterate over `items` and run `inner_action` once per item.

    Schema:
        items: list — required.
        inner_action: str — name of any registered action.
        inner_input: dict — template applied per iteration. Strings
            shaped `{{ item.<path> }}` or `{{ index }}` are resolved
            against the loop binding `{item, index}`. Literals pass
            through.
        max_items: int = 1000 (hard cap 5000).
        on_error: "continue" (default) | "abort".

    Returns:
        {count: int, results: [{index, output}], errors: [{index, error}]}

    Idempotency caveat (v1): the whole loop is one AutomationStepRun.
    A crash mid-loop replays the entire loop from index 0 — inner
    actions that mutate external state (e.g. crm.create_contact)
    should be designed to dedupe by stable identifiers (email, etc.).
    Per-iteration idempotency_keys land with the M11 sub-graph loop.
    """
    items = payload.get("items")
    if not isinstance(items, list):
        raise ActionError("crm.loop requires items: list")

    inner_name = payload.get("inner_action")
    if not isinstance(inner_name, str) or not inner_name:
        raise ActionError("crm.loop requires inner_action: str")

    inner_input_template = payload.get("inner_input") or {}
    if not isinstance(inner_input_template, dict):
        raise ActionError("crm.loop inner_input must be an object")

    max_items = int(payload.get("max_items") or 1000)
    if max_items > _LOOP_MAX_ITEMS_HARD_CAP:
        raise ActionError(
            f"crm.loop max_items capped at {_LOOP_MAX_ITEMS_HARD_CAP}, got {max_items}"
        )
    if len(items) > max_items:
        raise ActionError(f"crm.loop got {len(items)} items, max is {max_items}")

    on_error = str(payload.get("on_error") or "continue")
    if on_error not in {"continue", "abort"}:
        raise ActionError("crm.loop on_error must be 'continue' or 'abort'")

    # Guard against recursion — a loop calling crm.loop would explode quickly.
    if inner_name == "crm.loop":
        raise ActionError("crm.loop cannot nest itself; use sub-graphs instead")

    inner_handler = get(inner_name)

    results: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for idx, item in enumerate(items):
        bindings = {"item": item, "index": idx}
        try:
            resolved = _resolve_loop_template(inner_input_template, bindings)
        except Exception as exc:  # noqa: BLE001 — template failures are user-data errors
            errors.append({"index": idx, "error": f"template error: {exc}"})
            if on_error == "abort":
                raise ActionError(
                    f"crm.loop aborted at item {idx} during template resolve: {exc}"
                ) from exc
            continue

        try:
            output = inner_handler(workspace, resolved)
            results.append({"index": idx, "output": output})
        except Exception as exc:  # noqa: BLE001 — surface any inner failure
            errors.append({"index": idx, "error": str(exc)})
            if on_error == "abort":
                raise ActionError(
                    f"crm.loop aborted at item {idx}: {exc}"
                ) from exc

    return {
        "count": len(items),
        "results": results,
        "errors": errors,
    }


# --- M9.S2 phase 3: CRM mutation actions ---------------------------------------


_CONTACT_PATCHABLE_FIELDS = {
    "first_name",
    "last_name",
    "primary_email",
    "phones",
    "title",
    "company_id",
    "owner_id",
    "lifecycle_stage",
    "source",
    "custom",
    "tags",
}

_COMPANY_PATCHABLE_FIELDS = {
    "name",
    "domain",
    "size_band",
    "industry",
    "owner_id",
    "custom",
    "tags",
}

_DEAL_PATCHABLE_FIELDS = {
    "name",
    "stage_id",
    "value_cents",
    "currency",
    "expected_close",
    "contact_id",
    "company_id",
    "owner_id",
    "custom",
    "tags",
}


def _apply_patch(instance, patch: dict[str, Any], allowed: set[str], *, action_name: str):  # type: ignore[no-untyped-def]
    """Apply `patch` onto `instance` for fields in `allowed` only. Returns
    the list of fields that actually changed (subset for save's
    `update_fields`).
    """
    if not isinstance(patch, dict):
        raise ActionError(f"{action_name} requires patch: object")
    rejected = set(patch.keys()) - allowed
    if rejected:
        raise ActionError(
            f"{action_name}: cannot patch fields {sorted(rejected)} — "
            f"allowed: {sorted(allowed)}"
        )
    changed: list[str] = []
    for field, value in patch.items():
        current = getattr(instance, field, None)
        if current != value:
            setattr(instance, field, value)
            changed.append(field)
    return changed


@register("crm.update_contact")
def action_update_contact(workspace, payload: dict[str, Any]) -> dict[str, Any]:
    from apps.contacts.models import Contact

    contact_id = payload.get("contact_id")
    if not contact_id:
        raise ActionError("crm.update_contact requires contact_id")
    patch = payload.get("patch") or {}

    try:
        contact = Contact.objects.get(workspace=workspace, pk=contact_id, deleted_at__isnull=True)
    except Contact.DoesNotExist as exc:
        raise ActionError(f"crm.update_contact: contact {contact_id} not found") from exc

    changed = _apply_patch(contact, patch, _CONTACT_PATCHABLE_FIELDS, action_name="crm.update_contact")
    if changed:
        contact.save(update_fields=changed)
    return {"contact_id": contact.id, "updated_fields": changed}


@register("crm.create_company")
def action_create_company(workspace, payload: dict[str, Any]) -> dict[str, Any]:
    from apps.companies.models import Company

    name = payload.get("name")
    if not name:
        raise ActionError("crm.create_company requires name")
    if "created_by_id" not in payload:
        raise ActionError("crm.create_company requires created_by_id")

    company = Company.objects.create(
        workspace=workspace,
        name=name,
        domain=payload.get("domain", ""),
        size_band=payload.get("size_band", ""),
        industry=payload.get("industry", ""),
        custom=payload.get("custom", {}),
        tags=payload.get("tags", []),
        created_by_id=payload["created_by_id"],
    )
    return {"company_id": company.id, "name": company.name, "domain": company.domain}


@register("crm.update_company")
def action_update_company(workspace, payload: dict[str, Any]) -> dict[str, Any]:
    from apps.companies.models import Company

    company_id = payload.get("company_id")
    if not company_id:
        raise ActionError("crm.update_company requires company_id")
    patch = payload.get("patch") or {}

    try:
        company = Company.objects.get(workspace=workspace, pk=company_id, deleted_at__isnull=True)
    except Company.DoesNotExist as exc:
        raise ActionError(f"crm.update_company: company {company_id} not found") from exc

    changed = _apply_patch(company, patch, _COMPANY_PATCHABLE_FIELDS, action_name="crm.update_company")
    if changed:
        company.save(update_fields=changed)
    return {"company_id": company.id, "updated_fields": changed}


@register("crm.create_deal")
def action_create_deal(workspace, payload: dict[str, Any]) -> dict[str, Any]:
    from apps.deals.models import Deal, Pipeline

    if "name" not in payload:
        raise ActionError("crm.create_deal requires name")
    if "pipeline_id" not in payload:
        raise ActionError("crm.create_deal requires pipeline_id")
    if "stage_id" not in payload:
        raise ActionError("crm.create_deal requires stage_id")
    if "created_by_id" not in payload:
        raise ActionError("crm.create_deal requires created_by_id")

    try:
        pipeline = Pipeline.objects.get(workspace=workspace, pk=payload["pipeline_id"])
    except Pipeline.DoesNotExist as exc:
        raise ActionError(
            f"crm.create_deal: pipeline {payload['pipeline_id']} not found"
        ) from exc

    valid_stages = {s["id"] for s in (pipeline.stages or [])}
    if payload["stage_id"] not in valid_stages:
        raise ActionError(
            f"crm.create_deal: stage_id {payload['stage_id']!r} not in pipeline "
            f"(valid: {sorted(valid_stages)})"
        )

    deal = Deal.objects.create(
        workspace=workspace,
        name=payload["name"],
        pipeline=pipeline,
        stage_id=payload["stage_id"],
        value_cents=int(payload.get("value_cents", 0)),
        currency=payload.get("currency", "USD"),
        expected_close=payload.get("expected_close") or None,
        contact_id=payload.get("contact_id"),
        company_id=payload.get("company_id"),
        owner_id=payload.get("owner_id"),
        custom=payload.get("custom", {}),
        tags=payload.get("tags", []),
        created_by_id=payload["created_by_id"],
    )
    return {"deal_id": deal.id, "name": deal.name, "stage_id": deal.stage_id}


@register("crm.update_deal")
def action_update_deal(workspace, payload: dict[str, Any]) -> dict[str, Any]:
    from apps.deals.models import Deal

    deal_id = payload.get("deal_id")
    if not deal_id:
        raise ActionError("crm.update_deal requires deal_id")
    patch = payload.get("patch") or {}

    try:
        deal = Deal.objects.get(workspace=workspace, pk=deal_id, deleted_at__isnull=True)
    except Deal.DoesNotExist as exc:
        raise ActionError(f"crm.update_deal: deal {deal_id} not found") from exc

    changed = _apply_patch(deal, patch, _DEAL_PATCHABLE_FIELDS, action_name="crm.update_deal")
    if changed:
        deal.save(update_fields=changed)
    return {"deal_id": deal.id, "updated_fields": changed}


_TASK_RELATED_TYPES = {"contact", "company", "deal", "task", "note"}


@register("crm.create_task")
def action_create_task(workspace, payload: dict[str, Any]) -> dict[str, Any]:
    from apps.tasks.models import Task

    if "title" not in payload:
        raise ActionError("crm.create_task requires title")
    if "related_type" not in payload or "related_id" not in payload:
        raise ActionError("crm.create_task requires related_type and related_id")
    if "created_by_id" not in payload:
        raise ActionError("crm.create_task requires created_by_id")
    if payload["related_type"] not in _TASK_RELATED_TYPES:
        raise ActionError(
            f"crm.create_task: related_type {payload['related_type']!r} must be one of "
            f"{sorted(_TASK_RELATED_TYPES)}"
        )

    task = Task.objects.create(
        workspace=workspace,
        title=payload["title"],
        description=payload.get("description", ""),
        due_at=payload.get("due_at") or None,
        related_type=payload["related_type"],
        related_id=int(payload["related_id"]),
        status=payload.get("status", "open"),
        priority=payload.get("priority", "medium"),
        owner_id=payload.get("owner_id"),
        custom=payload.get("custom", {}),
        created_by_id=payload["created_by_id"],
    )
    return {"task_id": task.id, "title": task.title, "status": task.status}


@register("crm.create_note")
def action_create_note(workspace, payload: dict[str, Any]) -> dict[str, Any]:
    from apps.notes.models import Note

    if not payload.get("body_md"):
        raise ActionError("crm.create_note requires body_md")
    if "related_type" not in payload or "related_id" not in payload:
        raise ActionError("crm.create_note requires related_type and related_id")
    if "author_id" not in payload:
        raise ActionError("crm.create_note requires author_id")
    if payload["related_type"] not in _TASK_RELATED_TYPES:
        raise ActionError(
            f"crm.create_note: related_type {payload['related_type']!r} must be one of "
            f"{sorted(_TASK_RELATED_TYPES)}"
        )

    note = Note.objects.create(
        workspace=workspace,
        body_md=payload["body_md"],
        related_type=payload["related_type"],
        related_id=int(payload["related_id"]),
        author_id=payload["author_id"],
    )
    return {"note_id": note.id, "related_type": note.related_type, "related_id": note.related_id}


def _resolve_loop_template(value: Any, bindings: dict[str, Any]) -> Any:
    """Resolve `{{ item.<path> }}` and `{{ index }}` references against
    the loop binding. Other strings pass through. Recurses into dicts +
    lists so nested templates work."""
    if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
        path = value[2:-2].strip()
        if path == "index":
            return bindings.get("index")
        if path == "item":
            return bindings.get("item")
        if path.startswith("item."):
            current: Any = bindings.get("item")
            for part in path.split(".")[1:]:
                if isinstance(current, dict):
                    current = current.get(part)
                else:
                    return None
            return current
        return None
    if isinstance(value, dict):
        return {k: _resolve_loop_template(v, bindings) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve_loop_template(v, bindings) for v in value]
    return value
