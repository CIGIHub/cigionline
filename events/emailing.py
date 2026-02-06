from __future__ import annotations

import html
from typing import TYPE_CHECKING

import pytz
from django.conf import settings
from django.template.loader import render_to_string
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from .email_rendering import render_email_subject, render_streamfield_email_html

if TYPE_CHECKING:
    from .models import Registrant, EmailTemplate


def _event_email_merge_vars(event) -> dict:
    """Pre-format event date/time/location merge vars for email templates.

    We expose strings (not datetimes) to keep templates simple and consistent.
    """

    # --- Date/time ---
    # For editor-facing email merge vars we want the *wall-clock time* that was
    # entered in the Event admin (i.e., the event's selected `time_zone`).
    #
    # In this codebase, `publishing_date` / `event_end` are typically stored as
    # UTC datetimes (Django/Wagtail behaviour with USE_TZ=True), and the admin
    # displays them in the site's configured timezone.
    #
    # Therefore: treat the stored values as UTC and convert them to the event's
    # configured timezone for display.
    #
    # NOTE: We intentionally do *not* use EventPage.event_start_time_utc here.
    # That property exists to work around legacy storage assumptions and can
    # shift the wall-clock time relative to what editors see in the admin.
    start_utc = getattr(event, "publishing_date", None)
    end_utc = getattr(event, "event_end", None)

    tz_name = getattr(event, "time_zone", None) or "America/Toronto"
    try:
        tz = pytz.timezone(tz_name)
    except Exception:
        tz = None

    def _to_local(dt):
        if not dt:
            return None
        try:
            if tz:
                return dt.astimezone(tz)
        except Exception:
            pass
        return dt

    start_local = _to_local(start_utc)
    end_local = _to_local(end_utc)

    event_date = start_local.strftime("%B %-d, %Y") if start_local else ""

    def _fmt_time(dt):
        if not dt:
            return ""
        return dt.strftime("%-I:%M %p").lstrip("0")

    start_time = _fmt_time(start_local)
    end_time = _fmt_time(end_local)
    event_time = start_time if not end_time else f"{start_time} – {end_time}"

    event_timezone = getattr(event, "time_zone_label", "") or ""
    event_datetime = " · ".join([x for x in [event_date, event_time] if x])
    if event_timezone:
        event_datetime = (event_datetime + f" ({event_timezone})").strip()

    # --- Location ---
    event_format = getattr(event, "event_format", "")
    location_name = getattr(event, "location_name", "") or ""

    # Prefer model helper if available.
    location_address = ""
    try:
        if hasattr(event, "location_string"):
            location_address = event.location_string() or ""
    except Exception:
        location_address = ""

    location_map_url = ""
    try:
        if hasattr(event, "location_map_url"):
            location_map_url = event.location_map_url() or ""
    except Exception:
        location_map_url = ""

    # For virtual events, show a simple "Virtual" label.
    location_display = ""
    if (event_format or "").lower() == "virtual":
        location_display = "Virtual"
    else:
        parts = [location_name, location_address]
        location_display = ", ".join([p for p in parts if p])

    return {
        "event_date": event_date,
        "event_time": event_time,
        "event_timezone": event_timezone,
        "event_datetime": event_datetime,
        "event_location_name": location_name,
        "event_location_address": location_address,
        "event_location_map_url": location_map_url,
        "event_location": location_display,
    }


def _render_registrant_answers(registrant) -> tuple[str, str]:
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
        kind = ""
        if answer_key.endswith("__details"):
            base = answer_key[: -len("__details")]
            kind = "Details"
        elif answer_key.endswith("__other"):
            base = answer_key[: -len("__other")]
            kind = "Other"

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
                    base_label = ff.conditional_details_label or ff.label
                else:
                    base_label = ff.label or answer_key

                if kind:
                    # Inline qualifier reads better than parentheses in emails
                    return f"{base_label} — {kind}"
                return base_label
        except Exception:
            pass

        # If we can't resolve the UUID to a current RegistrationFormField (e.g.
        # form template has changed since this registrant submitted), avoid showing
        # raw UUIDs in email. Use a neutral fallback label instead.
        if kind:
            return f"Additional question — {kind}"
        return "Additional question"

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


def send_event_campaign_email(campaign, registrant) -> None:
    """Send one scheduled EmailCampaign email to a registrant.

    Creates an EmailCampaignSend row to ensure idempotency.
    """

    from .models import EmailCampaignSend

    api_key = settings.SENDGRID_API_KEY

    event = campaign.event
    template_obj = campaign.template

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
    ctx.update(_event_email_merge_vars(event))

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


def _render_email_body(template_obj, ctx: dict) -> tuple[str, str]:
    # Backwards-compatible wrapper.
    return render_streamfield_email_html(template_obj=template_obj, ctx=ctx)


def send_confirmation_email(registrant, confirmed: bool) -> None:
    api_key = settings.SENDGRID_API_KEY

    event = registrant.event
    # Allow per-registration-type overrides (fall back to event defaults).
    reg_type = getattr(registrant, "registration_type", None)
    if confirmed:
        template_obj = (
            getattr(reg_type, "confirmation_template_override", None)
            if reg_type
            else None
        ) or event.confirmation_template
    else:
        template_obj = (
            getattr(reg_type, "waitlist_template_override", None)
            if reg_type
            else None
        ) or event.waitlist_template

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
    ctx.update(_event_email_merge_vars(event))

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


def send_duplicate_registration_manage_email(registrant) -> None:
    """Email a registrant a management link when they attempt to re-register.

    This is intentionally *not* editor-overridable: it's a security/privacy
    control and should remain consistent.
    """

    api_key = settings.SENDGRID_API_KEY
    event = registrant.event

    # Build a fresh self-service link.
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
        "registration_type": getattr(registrant, "registration_type", None),
        "manage_url": manage_url,
    }
    ctx.update(_event_email_merge_vars(event))

    subject = render_email_subject(
        "Manage your registration — {{ event.title }}",
        ctx,
    )

    # Keep the content intentionally minimal and stable, but render it through
    # the shared email wrapper for consistent styling.
    class _StaticTemplate:
        body = [
            ("heading", {"text": "Manage your registration", "level": "h2"}),
            (
                "paragraph",
                (
                    f"<p>It looks like you (or someone using your email address) tried to register again for <strong>{html.escape(event.title)}</strong>. "
                    "To review or update your registration, use the button above.</p>"
                ),
            ),
            ("paragraph", "<p>If you didn't request this, you can ignore this email.</p>"),
        ]

    # Adapt the wrapper template's `{% for block in body %}` expectations.
    # It uses `block.block_type` and `block.value`.
    from dataclasses import dataclass

    @dataclass
    class _Block:
        block_type: str
        value: object

    template_obj = _StaticTemplate()
    template_obj.body = [_Block(t, v) for (t, v) in template_obj.body]

    html_body, text = render_streamfield_email_html(template_obj=template_obj, ctx=ctx)

    message = Mail(
        from_email=settings.SENDGRID_FROM_EMAIL_EVENTS,
        to_emails=registrant.email,
        subject=subject,
        plain_text_content=text,
        html_content=html_body,
    )

    sg = SendGridAPIClient(api_key)
    response = sg.send(message)
    if response.status_code != 202:
        raise RuntimeError(f"Failed to send email, status code: {response.status_code}")
