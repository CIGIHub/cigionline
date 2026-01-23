from __future__ import annotations

from django.conf import settings
from django.template import Context, Template
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from .models import Registrant, EmailTemplate


def _render_subject(subject_template: str, ctx: dict) -> str:
    return Template(subject_template or "").render(Context(ctx)).strip()


def _render_email_body(template_obj: EmailTemplate, ctx: dict) -> tuple[str, str]:
    """
    Returns (html, text). Renders StreamField to HTML, then produces a text fallback.
    """
    html = render_to_string(
        "events/emails/email_template_body.html",
        {"body": template_obj.body, **ctx},
    ).strip()

    html = Template(html).render(Context(ctx))

    text = strip_tags(html)
    return html, text


def send_confirmation_email(registrant: Registrant, confirmed: bool) -> None:
    api_key = settings.SENDGRID_API_KEY

    event = registrant.event
    template_obj = event.confirmed_template if confirmed else event.waitlist_template

    ctx = {
        "event": event,
        "registrant": registrant,
        "registration_type": registrant.registration_type,
        "confirmed": confirmed,
        "status_label": "CONFIRMED ✅" if confirmed else "WAITLISTED ⏳",
    }

    if template_obj:
        subject = _render_subject(template_obj.subject, ctx)
        html, text = _render_email_body(template_obj, ctx)
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
