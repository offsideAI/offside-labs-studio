"""End-to-end auth tests covering M1 acceptance criteria.

Maps to TC-1, TC-2, TC-3 in TESTING.md. Email verification is mandatory
in our allauth config, so the test bypasses the verification email by
flipping EmailAddress.verified directly — that's the documented test
pattern for allauth-based auth in DRF.
"""

from __future__ import annotations

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_signup_login_me_flow() -> None:
    client = APIClient()

    # 1. Register.
    register_resp = client.post(
        "/api/auth/registration/",
        {
            "email": "test@example.com",
            "password1": "VerySecurePass123!",
            "password2": "VerySecurePass123!",
            "full_name": "Test User",
        },
        format="json",
    )
    assert register_resp.status_code in (
        status.HTTP_201_CREATED,
        status.HTTP_204_NO_CONTENT,
    ), register_resp.content

    # 2. With email-verification mandatory, manually mark the address verified
    #    so the login works (the alternative is to parse the verification email).
    from allauth.account.models import EmailAddress

    addr = EmailAddress.objects.get(email="test@example.com")
    addr.verified = True
    addr.primary = True
    addr.save(update_fields=["verified", "primary"])

    # 3. Log in.
    login_resp = client.post(
        "/api/auth/login/",
        {"email": "test@example.com", "password": "VerySecurePass123!"},
        format="json",
    )
    assert login_resp.status_code == status.HTTP_200_OK, login_resp.content
    body = login_resp.json()
    assert "access" in body
    assert "refresh" in body
    access_token = body["access"]

    # 4. /api/auth/user/ returns the current user.
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    me_resp = client.get("/api/auth/user/")
    assert me_resp.status_code == status.HTTP_200_OK, me_resp.content
    me = me_resp.json()
    assert me["email"] == "test@example.com"
    assert me["full_name"] == "Test User"


@pytest.mark.django_db
def test_unauthenticated_me_returns_401() -> None:
    client = APIClient()
    resp = client.get("/api/auth/user/")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_celery_ping_smoke() -> None:
    """The ping task imports cleanly and runs in-process via .apply()."""
    from offside_crm.celery import ping

    result = ping.apply()
    assert result.successful()
    assert "pong" in result.get()


def test_openapi_schema_endpoint() -> None:
    """The OpenAPI schema is publicly servable so codegen works without auth."""
    client = APIClient()
    resp = client.get("/api/schema/")
    assert resp.status_code == status.HTTP_200_OK
    # Schema is YAML by default; quick sanity check.
    content = resp.content.decode("utf-8")
    assert "openapi:" in content or "openapi" in content.lower()
    assert "Offside CRM API" in content
