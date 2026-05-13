"""crm.http.request action tests (M9.S2 phase 1, TC-65).

We don't hit the real network. `httpx.Client.request` is monkey-patched
with a fake that returns a `FakeResponse` and captures the outbound
method / URL / headers / body so tests assert the wire shape.
"""

from __future__ import annotations

import base64
import json
from typing import Any

import pytest

from apps.automations import actions
from apps.automations.exceptions import ActionError


class FakeResponse:
    def __init__(
        self,
        *,
        status_code: int = 200,
        headers: dict | None = None,
        text: str = "",
        json_body: Any = None,
    ) -> None:
        self.status_code = status_code
        self.headers = headers or {"content-type": "application/json"}
        self._text = text
        self._json_body = json_body

    def json(self):  # type: ignore[no-untyped-def]
        if self._json_body is not None:
            return self._json_body
        # Mimic httpx.Response.json() — raises if body isn't valid JSON.
        return json.loads(self._text)

    @property
    def text(self) -> str:
        if self._text:
            return self._text
        return json.dumps(self._json_body) if self._json_body is not None else ""


@pytest.fixture
def captured(monkeypatch):  # type: ignore[no-untyped-def]
    """Patch httpx.Client.request and capture outbound shape.

    The returned dict is mutated by the patched request fn. Tests that
    want to control the response should set `cap["response"]` before
    invoking the action.
    """
    import httpx

    cap: dict[str, Any] = {
        "response": FakeResponse(json_body={"ok": True}),
    }

    def fake_request(self, method: str, url: str, **kwargs):  # type: ignore[no-untyped-def]
        cap["method"] = method
        cap["url"] = url
        cap["headers"] = dict(kwargs.get("headers") or {})
        cap["json"] = kwargs.get("json")
        cap["content"] = kwargs.get("content")
        return cap["response"]

    monkeypatch.setattr(httpx.Client, "request", fake_request)
    return cap


def test_get_with_no_auth(captured) -> None:  # type: ignore[no-untyped-def]
    result = actions.action_http_request(
        None,
        {"url": "https://api.example.com/ping"},
    )
    assert captured["method"] == "GET"
    assert captured["url"] == "https://api.example.com/ping"
    assert "Authorization" not in captured["headers"]
    assert result["status_code"] == 200
    assert result["body"] == {"ok": True}


def test_bearer_auth_sets_authorization_header(captured) -> None:  # type: ignore[no-untyped-def]
    actions.action_http_request(
        None,
        {
            "url": "https://api.example.com/x",
            "auth": {"type": "bearer", "token": "sk_live_abc"},
        },
    )
    assert captured["headers"]["Authorization"] == "Bearer sk_live_abc"


def test_basic_auth_encodes_credentials(captured) -> None:  # type: ignore[no-untyped-def]
    actions.action_http_request(
        None,
        {
            "url": "https://api.example.com/x",
            "auth": {"type": "basic", "username": "alice", "password": "s3cret"},
        },
    )
    expected = base64.b64encode(b"alice:s3cret").decode("ascii")
    assert captured["headers"]["Authorization"] == f"Basic {expected}"


def test_custom_header_auth(captured) -> None:  # type: ignore[no-untyped-def]
    actions.action_http_request(
        None,
        {
            "url": "https://api.example.com/x",
            "auth": {"type": "header", "name": "X-API-Key", "value": "topsecret"},
        },
    )
    assert captured["headers"]["X-API-Key"] == "topsecret"


def test_post_with_json_body(captured) -> None:  # type: ignore[no-untyped-def]
    actions.action_http_request(
        None,
        {
            "url": "https://api.example.com/x",
            "method": "POST",
            "body": {"hello": "world"},
        },
    )
    assert captured["method"] == "POST"
    assert captured["json"] == {"hello": "world"}
    assert captured["content"] is None


def test_post_with_string_body(captured) -> None:  # type: ignore[no-untyped-def]
    actions.action_http_request(
        None,
        {
            "url": "https://api.example.com/x",
            "method": "POST",
            "body": "raw=text",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
        },
    )
    assert captured["content"] == "raw=text"
    assert captured["json"] is None
    assert captured["headers"]["Content-Type"] == "application/x-www-form-urlencoded"


def test_response_falls_back_to_text_when_not_json(captured) -> None:  # type: ignore[no-untyped-def]
    captured["response"] = FakeResponse(
        text="<html>not json</html>",
        headers={"content-type": "text/html"},
    )
    result = actions.action_http_request(
        None, {"url": "https://api.example.com/x"}
    )
    assert result["body"] == "<html>not json</html>"


def test_expect_json_false_returns_raw_text(captured) -> None:  # type: ignore[no-untyped-def]
    captured["response"] = FakeResponse(json_body={"ok": True})
    result = actions.action_http_request(
        None,
        {"url": "https://api.example.com/x", "expect_json": False},
    )
    assert isinstance(result["body"], str)


def test_rejects_non_http_url() -> None:
    with pytest.raises(ActionError):
        actions.action_http_request(None, {"url": "file:///etc/passwd"})


def test_rejects_missing_url() -> None:
    with pytest.raises(ActionError):
        actions.action_http_request(None, {"method": "GET"})


def test_rejects_unknown_method() -> None:
    with pytest.raises(ActionError):
        actions.action_http_request(
            None, {"url": "https://api.example.com/x", "method": "PROPFIND"}
        )


def test_rejects_bad_timeout() -> None:
    with pytest.raises(ActionError):
        actions.action_http_request(
            None,
            {"url": "https://api.example.com/x", "timeout_seconds": 1000},
        )


def test_bearer_auth_requires_token() -> None:
    with pytest.raises(ActionError):
        actions.action_http_request(
            None,
            {
                "url": "https://api.example.com/x",
                "auth": {"type": "bearer"},
            },
        )


def test_request_error_becomes_action_error(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    import httpx

    def raise_request_error(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        raise httpx.ConnectError("connection refused")

    monkeypatch.setattr(httpx.Client, "request", raise_request_error)

    with pytest.raises(ActionError) as excinfo:
        actions.action_http_request(None, {"url": "https://api.example.com/x"})
    assert "connection refused" in str(excinfo.value)


def test_response_body_truncated_when_huge(captured) -> None:  # type: ignore[no-untyped-def]
    huge = "x" * (300 * 1024)
    captured["response"] = FakeResponse(
        text=huge, headers={"content-type": "text/plain"}
    )
    result = actions.action_http_request(
        None, {"url": "https://api.example.com/x", "expect_json": False}
    )
    assert result["body"].endswith("…[truncated]")
    assert len(result["body"]) < len(huge)


def test_action_registered() -> None:
    assert "crm.http.request" in actions.all_names()
