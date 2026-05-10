"""Pytest config — runs Celery eagerly in tests so .delay() executes in-process."""

from __future__ import annotations


def pytest_configure(config) -> None:  # type: ignore[no-untyped-def]
    """Force Celery into eager mode after Django settings load."""
    from django.conf import settings

    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True
    # Use locmem email backend in tests so Resend isn't called.
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
