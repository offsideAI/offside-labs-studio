"""Celery tasks for workspace operations."""

from __future__ import annotations

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import Invitation


@shared_task(name="workspaces.send_invitation_email")
def send_invitation_email(invitation_id: int, accept_url_base: str) -> str:
    """Send the invitation magic-link email via Resend (configured in settings).

    `accept_url_base` is the frontend's accept-invite route, e.g.
    `https://app.offside.ai/accept-invite`. The token is appended.
    """
    invitation = Invitation.objects.select_related("workspace", "invited_by").get(pk=invitation_id)

    accept_url = f"{accept_url_base.rstrip('/')}/{invitation.token}"

    context = {
        "invitation": invitation,
        "accept_url": accept_url,
        "workspace_name": invitation.workspace.name,
        "invited_by_email": invitation.invited_by.email,
        "role_display": invitation.get_role_display(),  # type: ignore[attr-defined]
    }

    html_body = render_to_string("workspaces/invitation_email.html", context)
    text_body = strip_tags(html_body)

    message = EmailMultiAlternatives(
        subject=f"You're invited to join {invitation.workspace.name} on Offside CRM",
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[invitation.email],
    )
    message.attach_alternative(html_body, "text/html")
    message.send(fail_silently=False)

    return f"sent invitation {invitation.id} to {invitation.email}"
