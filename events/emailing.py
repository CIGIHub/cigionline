from __future__ import annotations
from django.core.mail import send_mail
from django.conf import settings

from .models import Registrant


def send_confirmation_email(registrant: Registrant, confirmed: bool) -> None:
    """
    Minimal placeholder. Swap to your ESP (SendGrid/SES) later.
    """
    subject = f"Registration {'confirmed' if confirmed else 'received'} — {registrant.event.title}"
    body = [
        f"Hi {registrant.first_name or registrant.email},",
        "",
        f"Thanks for registering for {registrant.event.title}.",
        "Status: " + ("CONFIRMED ✅" if confirmed else "WAITLISTED ⏳"),
    ]
    if confirmed:
        body.append("We look forward to seeing you!")
    else:
        body.append("We’ll notify you if a spot opens.")

    send_mail(
        subject=subject,
        message="\n".join(body),
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.org"),
        recipient_list=[registrant.email],
        fail_silently=True,
    )
