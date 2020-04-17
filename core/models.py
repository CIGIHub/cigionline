from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page


class HomePage(Page):
    """Singleton model for the home page."""

    max_count = 1
    subpage_types = [
        'core.BasicPage',
        'people.PersonListPage',
        'research.TopicListPage'
    ]
    templates = 'core/home_page.html'

    class Meta:
        verbose_name = 'Home Page'


class CorePage(Page):
    """Page with subtitle."""

    subtitle = RichTextField(blank=True, null=False, features=['bold', 'italic'])

    # Override content_panels to put the title panel within a MultiFieldPanel
    content_panels = [
        MultiFieldPanel(
            [
                FieldPanel('title'),
                FieldPanel('subtitle')
            ],
            heading='Title',
            classname='collapsible'
        )
    ]

    class Meta:
        abstract = True


class BasicPage(CorePage):
    """Page with StreamField body"""

    body = StreamField(
        [
            ('paragraph', blocks.RichTextBlock())
        ],
        blank=True,
    )

    content_panels = CorePage.content_panels + [
        MultiFieldPanel(
            [
                StreamFieldPanel('body')
            ],
            heading='Body',
            classname='collapsible'
        )
    ]
    parent_page_types = ['core.HomePage']
    subpage_types = ['core.BasicPage', 'people.PersonListPage']
    template = 'core/basic_page.html'

    class Meta:
        verbose_name = 'Basic Page'
        verbose_name_plural = 'Basic Pages'
