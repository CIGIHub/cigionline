from __future__ import annotations
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from .models import Registrant


def send_confirmation_email(registrant: Registrant, confirmed: bool) -> None:
    """
    Minimal placeholder. Swap to your ESP (SendGrid/SES) later.
    """
    api_key = settings.SENDGRID_API_KEY
    subject = f"Registration {'confirmed' if confirmed else 'received'} — {registrant.event.title}"
    lines = [
        f"Hi {registrant.first_name or registrant.email},",
        "",
        f"Thanks for registering for {registrant.event.title}.",
        "Status: " + ("CONFIRMED ✅" if confirmed else "WAITLISTED ⏳"),
    ]
    lines.append("We look forward to seeing you!" if confirmed else "We’ll notify you if a spot opens.")
    body_text = "\n".join(lines)

    message = Mail(
        from_email="jxu@cigionline.org",
        to_emails=registrant.email,
        subject=subject,
        plain_text_content=body_text,  # <-- must be a string
    )

    sg = SendGridAPIClient(api_key)
    response = sg.send(message)
    if response.status_code != 202:
        raise RuntimeError(f"Failed to send email, status code: {response.status_code}")
    return response
