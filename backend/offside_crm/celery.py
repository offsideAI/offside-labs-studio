"""Celery app for Offside CRM.

The workflow runtime (PLAN.md §7) layers a custom Django durable engine on
top of this Celery app. M7 lands the run-advancer task, the wake-up sweep
Beat schedule, and the action-handler registry.

Until then this module exists so `celery -A offside_crm worker` boots and
the `ping` smoke task proves the worker is alive.
"""

from __future__ import annotations

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "offside_crm.settings.dev")

app = Celery("offside_crm")

# CELERY_-prefixed settings come from Django settings; everything else is read
# from environment variables in the same module.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in every installed app's `tasks.py`.
app.autodiscover_tasks()


@app.task(bind=True, name="offside_crm.ping")
def ping(self) -> str:  # type: ignore[no-untyped-def]
    """Smoke task. `celery -A offside_crm call offside_crm.ping` should return a string."""
    return f"pong from worker (task_id={self.request.id})"
