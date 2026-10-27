from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import models
from wagtail.admin.panels import (
    FieldPanel,
    HelpPanel,
    MultiFieldPanel,
)
from wagtail.contrib.settings.models import (
    BaseGenericSetting,
    BaseSiteSetting,
    register_setting,
)
from wagtail.fields import RichTextField


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

    # General Inquiries form recipients (BugHerd #163). Blank falls back to the
    # venue list above, so the form works before this is configured.
    general_recipients_raw = models.TextField(
        blank=True,
        verbose_name="General inquiry recipients",
        help_text=(
            "Recipients for the General Inquiries form. One email per line "
            "(or comma separated). Leave blank to use the list above."
        ),
    )

    # Post-submit destinations (BugHerd #355): each form redirects to its
    # thank-you page. Blank keeps the old behaviour — back to the hosting
    # page with a success message.
    venue_thanks_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Venue rental thank-you page',
        help_text='Page shown after a venue rental inquiry is sent.',
    )
    general_thanks_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='General inquiry thank-you page',
        help_text='Page shown after a general inquiry is sent.',
    )

    panels = [
        HelpPanel(content="<p>These addresses will receive submissions from your embedded email form.</p>"),
        FieldPanel("recipients_raw"),
        FieldPanel("general_recipients_raw"),
        FieldPanel("venue_thanks_page"),
        FieldPanel("general_thanks_page"),
    ]

    class Meta:
        verbose_name = "Email form"

    @property
    def recipients(self) -> list[str]:
        """Parsed & trimmed list (no validation errors raised here)."""
        return _parse_recipients(self.recipients_raw)

    @property
    def general_recipients(self) -> list[str]:
        """General Inquiries list; the venue list is the fallback."""
        return _parse_recipients(self.general_recipients_raw) or self.recipients

    def clean(self):
        # Validate each address so mistakes are caught in the admin
        errors = {}
        for field in ("recipients_raw", "general_recipients_raw"):
            for addr in _parse_recipients(getattr(self, field)):
                try:
                    validate_email(addr)
                except ValidationError:
                    errors.setdefault(field, []).append(f"Invalid email: {addr}")
        if errors:
            raise ValidationError(errors)
        return super().clean()


@register_setting
class FooterSettings(BaseSiteSetting):
    """
    Settings -> Footer: authorable brand chrome for the design-system footer.

    The four link columns + legal links are authored as `menus.Menu` objects
    (slugs `footer-research`, `footer-experts-events`, `footer-digital-policy-hub`,
    `footer-about`, `footer-legal`) so they reuse the existing menu authoring UI.
    This model owns the non-menu chrome: logo, address, social URLs and the
    newsletter copy.
    """

    logo = models.ForeignKey(
        'images.CigionlineImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Footer logo (use the reverse / white version). Leave blank to fall back to the default CIGI logo.',
    )
    address = RichTextField(
        blank=True,
        features=['link'],
        default='<p>67 Erb Street West, Waterloo, ON<br/>Canada<br/>N2L 6C2</p>',
        help_text='Footer mailing address. Select text and use the link tool to link '
                  'part of the address (e.g. a map link).',
    )
    organization_name = models.CharField(
        max_length=255,
        blank=True,
        default='Centre for International Governance Innovation (CIGI)',
        help_text='Shown in the copyright line. The year is added automatically.',
    )
    newsletter_heading = models.CharField(
        max_length=255,
        blank=True,
        default='Subscribe to our newsletter',
    )
    newsletter_intro = models.TextField(
        blank=True,
        default='Get regular updates on our research and events in your inbox.',
    )
    newsletter_consent = RichTextField(
        blank=True,
        features=['link'],
        default='<p>By subscribing you agree to our <a href="/privacy-notice/">Privacy Policy</a>.</p>',
        help_text='Small print shown under the newsletter form.',
    )
    twitter_url = models.URLField(blank=True, default='https://x.com/cigionline', verbose_name='X (Twitter) URL')
    linkedin_url = models.URLField(blank=True, default='https://www.linkedin.com/company/cigionline/', verbose_name='LinkedIn URL')
    youtube_url = models.URLField(blank=True, default='https://www.youtube.com/user/cigivideos', verbose_name='YouTube URL')
    instagram_url = models.URLField(blank=True, default='https://www.instagram.com/cigionline/', verbose_name='Instagram URL')
    substack_url = models.URLField(blank=True, default='https://cigionlineorg.substack.com/', verbose_name='Substack URL')
    medium_url = models.URLField(blank=True, default='https://medium.com/centre-for-international-governance-innovation', verbose_name='Medium URL')

    panels = [
        FieldPanel('logo'),
        FieldPanel('address'),
        FieldPanel('organization_name'),
        MultiFieldPanel(
            [
                FieldPanel('newsletter_heading'),
                FieldPanel('newsletter_intro'),
                FieldPanel('newsletter_consent'),
            ],
            heading='Newsletter',
        ),
        MultiFieldPanel(
            [
                FieldPanel('twitter_url'),
                FieldPanel('linkedin_url'),
                FieldPanel('youtube_url'),
                FieldPanel('instagram_url'),
                FieldPanel('substack_url'),
                FieldPanel('medium_url'),
            ],
            heading='Social links',
        ),
    ]

    class Meta:
        verbose_name = 'Footer'


@register_setting
class HeaderSettings(BaseSiteSetting):
    """
    Settings -> Header: authorable brand chrome for the design-system header.

    The primary nav items + mega-menu panels are authored via the `primary-nav`
    Menu (Snippets -> Menus). This model owns the non-menu chrome: logo, the
    Newsletter button, and the search placeholder.
    """

    logo = models.ForeignKey(
        'images.CigionlineImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Header logo. Leave blank to fall back to the default CIGI brand mark.',
    )
    newsletter_label = models.CharField(
        max_length=64,
        blank=True,
        default='Newsletter Sign-Up',
        help_text='Text on the header newsletter button.',
    )
    newsletter_link = models.CharField(
        max_length=512,
        blank=True,
        default='/subscribe/',
        help_text='Where the newsletter button points (internal path or external URL).',
    )
    search_placeholder = models.CharField(
        max_length=64,
        blank=True,
        default='Search',
        help_text='Placeholder text in the header search field.',
    )

    panels = [
        FieldPanel('logo'),
        FieldPanel('newsletter_label'),
        FieldPanel('newsletter_link'),
        FieldPanel('search_placeholder'),
    ]

    class Meta:
        verbose_name = 'Header'


@register_setting(icon='folder-open-inverse')
class ArchiveSettings(BaseGenericSetting):
    """Settings -> Archive: the page untagged content trails back to (BugHerd #279).

    Articles, publications, multimedia and events that no current program owns
    show "Home > <this page's title>" (IA decision 2026-09-04, CIGI aligned
    2026-09-09). Site-wide on purpose: a per-Site setting saved on the editing
    host would never reach the public host, since the hero reads one row.
    Blank falls back to auto-detection (``core.archive``), so the crumb works
    without configuration.
    """

    archive_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text=(
            'Breadcrumb target for articles, publications, multimedia and events that are not '
            'tagged to a current program (Home > this page; the crumb shows the page title). '
            'Leave blank to use the published Basic page whose body has a Faceted Listing set '
            'to "Archive — content with no program". The header link is a menu item: '
            'Settings -> Menus.'
        ),
    )

    panels = [
        FieldPanel('archive_page'),
    ]

    class Meta:
        verbose_name = 'Archive'
