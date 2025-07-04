from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from streams.blocks import ParagraphBlock, FloatedBioBlock, CAIAIObjectivesBlock
from core.models import ShareablePageAbstract


class CAIAIHomePage(Page, ShareablePageAbstract):
    """Singleton model for the CAIAI home page."""

    body = StreamField(
        [
            ('paragraph', ParagraphBlock()),
            ('floated_bio', FloatedBioBlock()),
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
    subpage_types = [
        'caiai.CAIAIAboutPage',
        'caiai.CAIAIBioPage',
        'caiai.CAIAIRecommendationsPage',
    ]

    class Meta:
        verbose_name = 'CAIAI Home Page'


class CAIAIAboutPage(Page, ShareablePageAbstract):
    """Singleton model for the CAIAI about page."""

    body = StreamField(
        [
            ('paragraph', ParagraphBlock()),
            ('floated_bio', FloatedBioBlock()),
            ('caiai_objectives', CAIAIObjectivesBlock()),
        ],
        blank=True,
    )
    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]

    def get_template(self, request, *args, **kwargs):
        """Return the template for the CAIAI about page."""
        return 'caiai/about_page.html'

    max_count = 1

    class Meta:
        verbose_name = 'CAIAI About Page'


class CAIAIRecommendationsPage(Page, ShareablePageAbstract):
    """Singleton model for the CAIAI recommendations page."""

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
        """Return the template for the CAIAI recommendations page."""
        return 'caiai/recommendations_page.html'

    max_count = 1

    class Meta:
        verbose_name = 'CAIAI Recommendations Page'


class CAIAIBioPage(Page):
    """Singleton model for the CAIAI bio page."""

    body = StreamField(
        [
            ('paragraph', ParagraphBlock()),
            ('floated_bio', FloatedBioBlock()),
        ],
        blank=True,
    )
    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]

    def get_template(self, request, *args, **kwargs):
        """Return the template for the CAIAI bio page."""
        return 'caiai/bio_page.html'

    max_count = 1

    class Meta:
        verbose_name = 'CAIAI Bio Page'
