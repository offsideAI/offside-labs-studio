"""crm.loop action tests (M9.S2 phase 2).

Covers:
- Iterating over [a, b, c] runs the inner action 3 times.
- `{{ item.field }}` and `{{ index }}` templates resolve.
- Nested template inside dict/list.
- Empty items list → count=0.
- on_error="continue" collects errors but keeps going.
- on_error="abort" raises ActionError.
- max_items / hard-cap enforced.
- Bad inputs (non-list items, non-str inner_action, non-dict inner_input,
  unknown inner action) → ActionError.
- Recursion guard: crm.loop calling crm.loop rejected.
- Inner action sees the resolved input, not the raw template.
"""

from __future__ import annotations

import pytest

from apps.automations import actions
from apps.automations.exceptions import ActionError


@pytest.fixture(autouse=True)
def reset_capture():  # type: ignore[no-untyped-def]
    """Reset module-level test capture between tests."""
    yield


def test_iterates_over_three_items() -> None:
    captured: list[dict] = []

    @actions.register("test.capture.1")
    def _handler(ws, payload):  # type: ignore[no-untyped-def]
        captured.append(dict(payload))
        return {"got": payload.get("v")}

    try:
        result = actions.action_loop(
            None,
            {
                "items": [{"v": 1}, {"v": 2}, {"v": 3}],
                "inner_action": "test.capture.1",
                "inner_input": {"v": "{{ item.v }}"},
            },
        )
    finally:
        del actions._REGISTRY["test.capture.1"]

    assert result["count"] == 3
    assert [r["output"]["got"] for r in result["results"]] == [1, 2, 3]
    assert result["errors"] == []
    assert captured == [{"v": 1}, {"v": 2}, {"v": 3}]


def test_index_and_item_template_resolution() -> None:
    captured: list[dict] = []

    @actions.register("test.capture.2")
    def _handler(ws, payload):  # type: ignore[no-untyped-def]
        captured.append(dict(payload))
        return payload

    try:
        actions.action_loop(
            None,
            {
                "items": ["a", "b"],
                "inner_action": "test.capture.2",
                "inner_input": {
                    "i": "{{ index }}",
                    "raw_item": "{{ item }}",
                    "nested": {"deep": "{{ item }}"},
                    "literal": "stays",
                },
            },
        )
    finally:
        del actions._REGISTRY["test.capture.2"]

    assert captured == [
        {"i": 0, "raw_item": "a", "nested": {"deep": "a"}, "literal": "stays"},
        {"i": 1, "raw_item": "b", "nested": {"deep": "b"}, "literal": "stays"},
    ]


def test_dotted_item_path_resolution() -> None:
    captured: list[dict] = []

    @actions.register("test.capture.3")
    def _handler(ws, payload):  # type: ignore[no-untyped-def]
        captured.append(dict(payload))
        return payload

    try:
        actions.action_loop(
            None,
            {
                "items": [
                    {"contact": {"name": "Ada", "email": "ada@example.com"}},
                    {"contact": {"name": "Grace", "email": "grace@example.com"}},
                ],
                "inner_action": "test.capture.3",
                "inner_input": {
                    "email": "{{ item.contact.email }}",
                    "missing": "{{ item.contact.does_not_exist }}",
                },
            },
        )
    finally:
        del actions._REGISTRY["test.capture.3"]

    assert captured[0] == {"email": "ada@example.com", "missing": None}
    assert captured[1] == {"email": "grace@example.com", "missing": None}


def test_empty_items_list_returns_zero_count() -> None:
    result = actions.action_loop(
        None,
        {"items": [], "inner_action": "noop", "inner_input": {}},
    )
    assert result == {"count": 0, "results": [], "errors": []}


def test_on_error_continue_collects_failures() -> None:
    @actions.register("test.flaky")
    def _handler(ws, payload):  # type: ignore[no-untyped-def]
        if payload.get("v") == 2:
            raise RuntimeError("kaboom")
        return {"v": payload.get("v")}

    try:
        result = actions.action_loop(
            None,
            {
                "items": [{"v": 1}, {"v": 2}, {"v": 3}],
                "inner_action": "test.flaky",
                "inner_input": {"v": "{{ item.v }}"},
                # on_error defaults to "continue"
            },
        )
    finally:
        del actions._REGISTRY["test.flaky"]

    assert result["count"] == 3
    assert [r["output"]["v"] for r in result["results"]] == [1, 3]
    assert result["errors"] == [{"index": 1, "error": "kaboom"}]


def test_on_error_abort_raises() -> None:
    @actions.register("test.abort")
    def _handler(ws, payload):  # type: ignore[no-untyped-def]
        if payload.get("v") == 2:
            raise RuntimeError("nope")
        return {"v": payload.get("v")}

    try:
        with pytest.raises(ActionError) as excinfo:
            actions.action_loop(
                None,
                {
                    "items": [{"v": 1}, {"v": 2}, {"v": 3}],
                    "inner_action": "test.abort",
                    "inner_input": {"v": "{{ item.v }}"},
                    "on_error": "abort",
                },
            )
    finally:
        del actions._REGISTRY["test.abort"]

    assert "item 2" in str(excinfo.value) or "item 1" in str(excinfo.value)


def test_max_items_enforced() -> None:
    with pytest.raises(ActionError) as excinfo:
        actions.action_loop(
            None,
            {
                "items": list(range(50)),
                "inner_action": "noop",
                "inner_input": {},
                "max_items": 10,
            },
        )
    assert "max is 10" in str(excinfo.value)


def test_max_items_hard_cap() -> None:
    with pytest.raises(ActionError) as excinfo:
        actions.action_loop(
            None,
            {
                "items": [],
                "inner_action": "noop",
                "inner_input": {},
                "max_items": 999_999,
            },
        )
    assert "capped" in str(excinfo.value)


def test_rejects_non_list_items() -> None:
    with pytest.raises(ActionError):
        actions.action_loop(
            None, {"items": {"not": "a list"}, "inner_action": "noop", "inner_input": {}}
        )


def test_rejects_missing_inner_action() -> None:
    with pytest.raises(ActionError):
        actions.action_loop(None, {"items": [], "inner_input": {}})


def test_rejects_non_dict_inner_input() -> None:
    with pytest.raises(ActionError):
        actions.action_loop(
            None,
            {"items": [], "inner_action": "noop", "inner_input": "not a dict"},
        )


def test_rejects_unknown_inner_action() -> None:
    with pytest.raises(ActionError):
        actions.action_loop(
            None,
            {"items": [1], "inner_action": "does.not.exist", "inner_input": {}},
        )


def test_rejects_bad_on_error_value() -> None:
    with pytest.raises(ActionError):
        actions.action_loop(
            None,
            {
                "items": [],
                "inner_action": "noop",
                "inner_input": {},
                "on_error": "explode",
            },
        )


def test_loop_cannot_nest_itself() -> None:
    with pytest.raises(ActionError) as excinfo:
        actions.action_loop(
            None,
            {"items": [1], "inner_action": "crm.loop", "inner_input": {}},
        )
    assert "nest" in str(excinfo.value)


def test_action_registered() -> None:
    assert "crm.loop" in actions.all_names()