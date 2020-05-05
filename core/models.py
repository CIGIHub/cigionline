from django.db import models
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel


class HomePage(Page):
    """Singleton model for the home page."""

    max_count = 1
    subpage_types = [
        'core.BasicPage',
        'people.PeoplePage',
        'people.PersonListPage',
        'research.TopicListPage'
    ]
    templates = 'core/home_page.html'

    class Meta:
        verbose_name = 'Home Page'


class BasicPageAbstract(Page):
    """Page with subtitle."""

    body = StreamField(
        [
            ('paragraph', blocks.RichTextBlock()),
            ('image', ImageChooserBlock()),
            ('block_quote', blocks.StructBlock([
                ('quote', blocks.RichTextBlock(required=True)),
                ('quote_author', blocks.CharBlock(required=False)),
                ('author_title', blocks.CharBlock(required=False)),
                ('image', ImageChooserBlock(required=False)),
            ])),

        ],
        blank=True,
    )
    image_hero = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Hero Image',
        help_text='A large image to be displayed prominently on the page.',
    )
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
        ),
        MultiFieldPanel(
            [
                StreamFieldPanel('body'),
            ],
            heading='Body',
            classname='collapsible'
        ),
        MultiFieldPanel(
            [
                ImageChooserPanel('image_hero'),
            ],
            heading='Images',
            classname='collapsible collapsed',
        ),
    ]

    class Meta:
        abstract = True


class BasicPage(BasicPageAbstract):
    """Page with StreamField body"""

    related_files = StreamField(
        [
            ('file', DocumentChooserBlock()),
        ],
        blank=True,
    )

    content_panels = BasicPageAbstract.content_panels + [
        MultiFieldPanel(
            [
                StreamFieldPanel('related_files'),
            ],
            heading='Related Files',
            classname='collapsible collapsed',
        ),
    ]
    parent_page_types = ['core.BasicPage', 'core.HomePage']
    subpage_types = ['core.BasicPage', 'core.FundingPage', 'people.PersonListPage']
    template = 'core/basic_page.html'

    class Meta:
        verbose_name = 'Basic Page'
        verbose_name_plural = 'Basic Pages'


class FundingPage(BasicPageAbstract):
    """
    A special singleton page for /about/funding that contains a hardcoded
    table with the funding details.
    """

    max_count = 1
    parent_page_types = ['core.BasicPage']
    subpage_types = []
    templates = 'core/funding_page.html'

    class Meta:
        verbose_name = 'Funding Page'
