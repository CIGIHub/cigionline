from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from streams.blocks import ParagraphBlock


class CAIAIHomePage(Page):
    """Singleton model for the CAIAI home page."""

    body = StreamField(
        [
            ('paragraph', ParagraphBlock()),
        ],
        blank=True,
    )
    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]

    def get_template(self, request, *args, **kwargs):
        """Return the template for the CAIAI home page."""
        return 'caiai/home_page.html'

    max_count = 1

    class Meta:
        verbose_name = 'CAIAI Home Page'
