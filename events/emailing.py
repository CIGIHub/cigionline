from __future__ import annotations

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from .models import Registrant, EmailTemplate
from .email_rendering import render_email_subject, render_streamfield_email_html


def _render_subject(subject_template: str, ctx: dict) -> str:
    # Backwards-compatible wrapper (existing importers may rely on this name).
    return render_email_subject(subject_template, ctx)


def _render_email_body(template_obj: EmailTemplate, ctx: dict) -> tuple[str, str]:
    # Backwards-compatible wrapper.
    return render_streamfield_email_html(template_obj=template_obj, ctx=ctx)


def send_confirmation_email(registrant: Registrant, confirmed: bool) -> None:
    api_key = settings.SENDGRID_API_KEY

    event = registrant.event
    template_obj = event.confirmation_template if confirmed else event.waitlist_template

    # Build a self-service link the registrant can use to update/cancel.
    raw_token = registrant.ensure_manage_token()
    if not raw_token:
        # Token already existed; we can't recover the raw token (stored hashed).
        # Regenerate a fresh token so we can email a valid link.
        registrant.manage_token_hash = ""
        raw_token = registrant.ensure_manage_token()

    base = event.get_url(request=None) or ("/" + event.url_path.lstrip("/"))
    manage_url = f"{base}register/manage/?rid={registrant.pk}&t={raw_token}"

    ctx = {
        "event": event,
        "registrant": registrant,
        "registration_type": registrant.registration_type,
        "confirmed": confirmed,
        "status_label": "CONFIRMED ✅" if confirmed else "WAITLISTED ⏳",
        "manage_url": manage_url,
    }

    if template_obj:
        subject = render_email_subject(template_obj.subject, ctx)
        html, text = render_streamfield_email_html(template_obj=template_obj, ctx=ctx)
    else:
        subject = f"Registration {'confirmed' if confirmed else 'received'} — {event.title}"
        lines = [
            f"Hi {registrant.first_name or registrant.email},",
            "",
            f"Thanks for registering for {event.title}.",
            "Status: " + ("CONFIRMED ✅" if confirmed else "WAITLISTED ⏳"),
        ]
        lines.append("We look forward to seeing you!" if confirmed else "We’ll notify you if a spot opens.")
        text = "\n".join(lines)
        html = "<br>".join(lines)

    message = Mail(
        from_email=settings.SENDGRID_FROM_EMAIL_EVENTS,
        to_emails=registrant.email,
        subject=subject,
        plain_text_content=text,
        html_content=html,
    )

    sg = SendGridAPIClient(api_key)
    response = sg.send(message)
    if response.status_code != 202:
        raise RuntimeError(f"Failed to send email, status code: {response.status_code}")
