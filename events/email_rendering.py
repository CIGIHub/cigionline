from __future__ import annotations

"""Utilities to render Wagtail StreamField-based email templates.

Goals:
- Render StreamField content to HTML that works across common email clients.
- Keep the output simple (table-based wrapper template, minimal tags).
- Inline any CSS so clients that strip <style> still render reasonably.
"""

from django.template import Context, Template
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def render_email_subject(subject_template: str, ctx: dict) -> str:
    return Template(subject_template or "").render(Context(ctx)).strip()


def _inline_css(html: str) -> str:
    """Inline CSS using premailer if installed; otherwise return unchanged."""

    try:
        from premailer import transform

        return transform(
            html,
            remove_classes=True,
            keep_style_tags=False,
            include_star_selectors=False,
        )
    except Exception:
        # Premailer is optional; don't break email sending if it's missing.
        return html


def render_streamfield_email_html(*, template_obj, ctx: dict) -> tuple[str, str]:
    """Returns (html, text) for an EmailTemplate-like object with .body StreamField."""

    html = render_to_string(
        "events/emails/email_template_body.html",
        {"body": template_obj.body, **ctx},
    ).strip()

    # Second pass: allow merge variables inside stream content.
    html = Template(html).render(Context(ctx))

    html = _inline_css(html)
    text = strip_tags(html)
    return html, text
