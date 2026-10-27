from __future__ import annotations

import re
from dataclasses import dataclass

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils import timezone
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from .email_rendering import render_email_subject, render_streamfield_email_html
from .emailing import (
    _absolute_event_base,
    _event_email_merge_vars,
    _from_email,
    _render_registrant_answers,
)


def _split_tokens(value: str) -> list[str]:
    return [x.strip().lower() for x in (value or "").split(",") if x.strip()]


def _split_slugs(value: str) -> list[str]:
    return [x.strip() for x in (value or "").split(",") if x.strip()]


def parse_test_recipient_emails(value: str) -> list[str]:
    recipients: list[str] = []
    seen: set[str] = set()

    for email in re.split(r"[,;\s]+", value or ""):
        email = email.strip()
        if not email:
            continue

        try:
            validate_email(email)
        except ValidationError as exc:
            raise ValidationError(f"Invalid test recipient email: {email}") from exc

        normalized = email.lower()
        if normalized in seen:
            continue

        seen.add(normalized)
        recipients.append(email)

    return recipients


class _DummySite:
    def __init__(self, root_url: str):
        self.root_url = root_url


class _DummyEvent:
    title = "Sample Event"
    event_format = "virtual"
    location_name = ""
    time_zone = "America/Toronto"

    def __init__(self, root_url: str):
        self.publishing_date = timezone.now()
        self.event_end = timezone.now()
        self._site = _DummySite(root_url)

    @property
    def time_zone_label(self):
        return "EST (UTC-05:00)"

    @property
    def event_start_time_utc(self):
        return self.publishing_date

    @property
    def event_end_time_utc(self):
        return self.event_end

    def location_string(self):
        return ""

    def location_map_url(self):
        return ""

    def get_site(self):
        return self._site


class _DummyRegistrationType:
    name = "General"
    slug = "general"


class _DummyRegistrant:
    pk = "preview"
    first_name = "Jane"
    last_name = "Example"
    email = "jane@example.com"
    status = "confirmed"
    answers = {}

    def __init__(self, event, registration_type):
        self.event = event
        self.registration_type = registration_type


@dataclass(frozen=True)
class EmailCampaignPreview:
    subject: str
    html: str
    body_html: str
    event_title: str
    registrant_label: str
    using_real_registrant: bool


def _select_preview_registrant(*, event, include_statuses: str, include_type_slugs: str):
    if not event:
        return None

    registrants = (
        event.registrants.select_related("registration_type")
        .order_by("-created_at")
    )

    statuses = _split_tokens(include_statuses)
    if statuses:
        registrants = registrants.filter(status__in=statuses)

    type_slugs = _split_slugs(include_type_slugs)
    if type_slugs:
        registrants = registrants.filter(registration_type__slug__in=type_slugs)

    return registrants.first()


def _select_preview_registration_type(*, event, registrant):
    if registrant:
        return registrant.registration_type

    if event:
        rtype = event.registration_types.order_by("sort_order").first()
        if rtype:
            return rtype

    return _DummyRegistrationType()


def build_email_campaign_preview(
    *,
    request,
    template_obj,
    event=None,
    include_statuses: str = "",
    include_type_slugs: str = "",
) -> EmailCampaignPreview:
    root_url = request.build_absolute_uri("/").rstrip("/")
    preview_event = event or _DummyEvent(root_url)
    real_registrant = _select_preview_registrant(
        event=event,
        include_statuses=include_statuses,
        include_type_slugs=include_type_slugs,
    )
    registration_type = _select_preview_registration_type(
        event=event,
        registrant=real_registrant,
    )
    registrant = real_registrant or _DummyRegistrant(preview_event, registration_type)

    try:
        base = _absolute_event_base(preview_event)
    except Exception:
        base = root_url + "/events/sample-event/"

    manage_url = f"{base}register/manage/?rid={getattr(registrant, 'pk', 'preview')}&t=preview"

    ctx = {
        "event": preview_event,
        "registrant": registrant,
        "registration_type": registration_type,
        "confirmed": getattr(registrant, "status", "") == "confirmed",
        "status_label": (getattr(registrant, "status", "") or "confirmed").upper(),
        "manage_url": manage_url,
    }
    ctx.update(_event_email_merge_vars(preview_event))

    answers_html, answers_text = _render_registrant_answers(registrant)
    ctx["registrant_answers_html"] = answers_html
    ctx["registrant_answers_text"] = answers_text

    subject = render_email_subject(template_obj.subject, ctx)
    html, _text = render_streamfield_email_html(template_obj=template_obj, ctx=ctx)
    body_html = _extract_email_body(html)
    registrant_label = (
        f"{getattr(registrant, 'first_name', '')} {getattr(registrant, 'last_name', '')}".strip()
        or getattr(registrant, "email", "")
        or "sample registrant"
    )

    return EmailCampaignPreview(
        subject=subject,
        html=html,
        body_html=body_html,
        event_title=getattr(preview_event, "title", "Sample Event"),
        registrant_label=registrant_label,
        using_real_registrant=bool(real_registrant),
    )


def _extract_email_body(html: str) -> str:
    match = re.search(r"<body\b[^>]*>(?P<body>.*)</body>", html or "", re.IGNORECASE | re.DOTALL)
    if not match:
        return html
    return match.group("body").strip()


def send_email_campaign_test(*, request, campaign) -> list[str]:
    recipients = parse_test_recipient_emails(campaign.test_recipient_emails)
    if not recipients:
        raise ValidationError("Add at least one test recipient email address.")

    preview = build_email_campaign_preview(
        request=request,
        template_obj=campaign.template,
        event=campaign.event,
        include_statuses=campaign.include_statuses,
        include_type_slugs=campaign.include_type_slugs,
    )

    subject = f"[TEST] {preview.subject}"
    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)

    for recipient in recipients:
        message = Mail(
            from_email=_from_email(),
            to_emails=recipient,
            subject=subject,
            plain_text_content=_html_to_text(preview.html),
            html_content=preview.html,
        )
        response = sg.send(message)
        if response.status_code != 202:
            raise RuntimeError(
                f"Failed to send test email to {recipient}, status code: {response.status_code}"
            )

    return recipients


def _html_to_text(html: str) -> str:
    from django.utils.html import strip_tags

    return strip_tags(html or "")
