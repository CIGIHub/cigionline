from __future__ import annotations

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from .models import Registrant, EmailTemplate
from .email_rendering import render_email_subject, render_streamfield_email_html


def _render_registrant_answers(registrant: Registrant) -> tuple[str, str]:
    """Render the registrant's dynamic answers as (html, text).

    Intended for use as a merge variable inside email templates.
    """

    answers = registrant.answers
    if not isinstance(answers, dict) or not answers:
        return ("", "")

    def _fmt_value(v) -> str:
        if v is None or v == "" or v == [] or v == {}:
            return ""
        if isinstance(v, bool):
            return "Yes" if v else "No"
        if isinstance(v, (int, float)):
            # Avoid showing trailing .0 for whole numbers.
            if isinstance(v, float) and v.is_integer():
                return str(int(v))
            return str(v)
        if isinstance(v, (list, tuple)):
            parts = [p for p in (_fmt_value(x) for x in v) if p]
            return ", ".join(parts)
        if isinstance(v, dict):
            # File upload values from save_registrant_from_form
            if "name" in v:
                return str(v.get("name") or "")
            return str(v)
        return str(v)

    def _is_internal_key(k: str) -> bool:
        # Hide honeypot + internal conditional toggles.
        if k == "website":
            return True
        if k.endswith("__enabled"):
            return True
        return False

    def _label_for_key(answer_key: str) -> str:
        # Dynamic fields are stored as f_<uuid> plus optional suffixes like:
        #   __details (conditional_text)
        #   __other   (conditional_dropdown_other)
        if not answer_key.startswith("f_"):
            return answer_key

        base = answer_key
        suffix = ""
        if answer_key.endswith("__details"):
            base = answer_key[: -len("__details")]
            suffix = " (details)"
        elif answer_key.endswith("__other"):
            base = answer_key[: -len("__other")]
            suffix = " (other)"

        # base expected: f_<uuid>
        raw_uuid = base[2:]
        # Normalize UUID (strip braces) and validate before querying.
        try:
            import uuid

            uuid_obj = uuid.UUID(raw_uuid)
        except Exception:
            return answer_key
        try:
            # registrant.event.registration_form_template.fields uses UUIDField field_key
            ff = (
                registrant.event.registration_form_template.fields.filter(field_key=uuid_obj)
                .only("label", "conditional_details_label")
                .first()
            )
            if ff:
                # Prefer the configured conditional details label for __details
                if answer_key.endswith("__details") and getattr(ff, "conditional_details_label", ""):
                    return (ff.conditional_details_label or ff.label) + suffix
                return (ff.label or answer_key) + suffix
        except Exception:
            pass

        # If we can't resolve the UUID to a current RegistrationFormField (e.g.
        # form template has changed since this registrant submitted), avoid showing
        # raw UUIDs in email. Use a neutral fallback label instead.
        return "Additional question" + suffix

    # Drop internal keys + empties; resolve labels + format values.
    items: list[tuple[str, str]] = []
    for k, v in answers.items():
        if _is_internal_key(str(k)):
            continue

        # Don't repeat identity fields if they were (incorrectly) stored in answers.
        if str(k) in {"email", "first_name", "last_name"}:
            continue

        fv = _fmt_value(v)
        if not fv:
            continue

        label = _label_for_key(str(k))
        items.append((label, fv))

    if not items:
        return ("", "")

    # Keep output simple and email-client-safe.
    html = render_to_string(
        "events/emails/_registrant_answers.html",
        {"items": items},
    ).strip()

    text_lines = ["Registration details:"]
    for k, v in items:
        text_lines.append(f"- {k}: {v}")
    text = "\n".join(text_lines)

    return (html, text)


def send_event_campaign_email(campaign, registrant: Registrant) -> None:
    """Send one scheduled EmailCampaign email to a registrant.

    Creates an EmailCampaignSend row to ensure idempotency.
    """

    from .models import EmailCampaignSend

    api_key = settings.SENDGRID_API_KEY

    event = campaign.event
    template_obj: EmailTemplate = campaign.template

    raw_token = registrant.ensure_manage_token()
    if not raw_token:
        registrant.manage_token_hash = ""
        raw_token = registrant.ensure_manage_token()

    base = event.get_url(request=None) or ("/" + event.url_path.lstrip("/"))
    manage_url = f"{base}register/manage/?rid={registrant.pk}&t={raw_token}"

    ctx = {
        "event": event,
        "registrant": registrant,
        "registration_type": registrant.registration_type,
        "confirmed": registrant.status == Registrant.Status.CONFIRMED,
        "status_label": registrant.status.upper(),
        "manage_url": manage_url,
    }

    answers_html, answers_text = _render_registrant_answers(registrant)
    ctx["registrant_answers_html"] = answers_html
    ctx["registrant_answers_text"] = answers_text

    # Reserve send (idempotency). If it already exists, do nothing.
    send_obj, created = EmailCampaignSend.objects.get_or_create(
        campaign=campaign,
        registrant=registrant,
    )
    if not created:
        return

    subject = render_email_subject(template_obj.subject, ctx)
    html, text = render_streamfield_email_html(template_obj=template_obj, ctx=ctx)

    message = Mail(
        from_email=settings.SENDGRID_FROM_EMAIL_EVENTS,
        to_emails=registrant.email,
        subject=subject,
        plain_text_content=text,
        html_content=html,
    )

    sg = SendGridAPIClient(api_key)
    try:
        response = sg.send(message)
        if response.status_code != 202:
            raise RuntimeError(f"Failed to send email, status code: {response.status_code}")
    except Exception:
        # Don't leave a send marker behind if delivery failed.
        send_obj.delete()
        raise


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

    answers_html, answers_text = _render_registrant_answers(registrant)
    ctx["registrant_answers_html"] = answers_html
    ctx["registrant_answers_text"] = answers_text

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
