from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import models
from wagtail.admin.panels import (
    FieldPanel,
    HelpPanel,
)
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting


def _parse_recipients(raw: str) -> list[str]:
    """
    Split on newlines or commas, strip, and drop empties.
    """
    if not raw:
        return []
    parts = [p.strip() for chunk in raw.splitlines() for p in chunk.split(',')]
    return [p for p in parts if p]


@register_setting
class EmailFormSettings(BaseSiteSetting):
    """
    Settings -> Email form: per-site list of recipient emails for your embedded forms.
    """
    recipients_raw = models.TextField(
        blank=True,
        help_text=(
            "Enter one email per line (or comma separated). "
            "Example:\neditor@example.com\nwebmaster@example.org"
        ),
    )

    panels = [
        HelpPanel(content="<p>These addresses will receive submissions from your embedded email form.</p>"),
        FieldPanel("recipients_raw"),
    ]

    class Meta:
        verbose_name = "Email form"

    @property
    def recipients(self) -> list[str]:
        """Parsed & trimmed list (no validation errors raised here)."""
        return _parse_recipients(self.recipients_raw)

    def clean(self):
        # Validate each address so mistakes are caught in the admin
        errors = {}
        for addr in self.recipients:
            try:
                validate_email(addr)
            except ValidationError:
                errors.setdefault("recipients_raw", []).append(f"Invalid email: {addr}")
        if errors:
            raise ValidationError(errors)
        return super().clean()
