from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel


class HomePage(Page):
    """Singleton model for the home page."""

    max_count = 1
    subpage_types = [
        'core.BasicPage',
        'people.PeoplePage',
        'people.PersonListPage',
        'publications.PublicationListPage',
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
    submenu = models.ForeignKey(
        'menus.Menu',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Submenu',
        help_text='Select a submenu to appear in the right section of the hero.',
    )
    subtitle = RichTextField(blank=True, null=False, features=['bold', 'italic'])

    # Override content_panels to put the title panel within a MultiFieldPanel
    title_panel = MultiFieldPanel(
        [
            FieldPanel('title'),
            FieldPanel('subtitle')
        ],
        heading='Title',
        classname='collapsible'
    )
    body_panel = MultiFieldPanel(
        [
            StreamFieldPanel('body'),
        ],
        heading='Body',
        classname='collapsible'
    )
    images_panel = MultiFieldPanel(
        [
            ImageChooserPanel('image_hero'),
        ],
        heading='Images',
        classname='collapsible collapsed',
    )
    content_panels = [
        title_panel,
        body_panel,
        images_panel,
    ]

    class Meta:
        abstract = True


class ShareablePageAbstract(Page):
    social_title = models.CharField(blank=True, max_length=255)
    social_description = models.CharField(blank=True, max_length=255)
    image_social = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Social image',
        help_text='An image that is used when sharing on social media.',
    )

    promote_panels = Page.promote_panels + [
        MultiFieldPanel(
            [
                FieldPanel('social_title'),
                FieldPanel('social_description'),
                ImageChooserPanel('image_social'),
            ],
            heading='Social Media',
            classname='collapsible collapsed',
        ),
    ]

    settings_panels = Page.settings_panels + [
        MultiFieldPanel(
            [
                FieldPanel('submenu'),
            ],
            heading='Submenu',
            classname='collapsible collapsed',
        ),
    ]

    class Meta:
        abstract = True


class FeatureablePageAbstract(Page):
    feature_subtitle = models.CharField(blank=True, max_length=255)
    feature_title = models.CharField(blank=True, max_length=255)
    image_feature = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Feature image',
        help_text='Image used when featuring on landing pages such as the home page',
    )

    promote_panels = Page.promote_panels + [
        MultiFieldPanel(
            [
                FieldPanel('feature_title'),
                FieldPanel('feature_subtitle'),
                ImageChooserPanel('image_feature'),
            ],
            heading='Feature Information',
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
    subpage_types = ['core.AnnualReportListPage', 'core.BasicPage', 'core.FundingPage', 'people.PersonListPage']
    template = 'core/basic_page.html'

    class Meta:
        verbose_name = 'Page'
        verbose_name_plural = 'Pages'


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


class AnnualReportListPage(BasicPageAbstract):
    max_count = 1
    parent_page_types = ['core.BasicPage']
    subpage_types = ['core.AnnualReportPage']
    templates = 'core/annual_report_list_page.html'

    class Meta:
        verbose_name = 'Annual Report List Page'


class AnnualReportPage(FeatureablePageAbstract):
    """View annual report page"""

    image_poster = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Cover image',
        help_text='Poster sized image that is displayed in the featured section on the Annual Reports page.',
    )
    report_english = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    report_financial = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    report_french = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    report_interactive = models.CharField(
        blank=True,
        max_length=255,
        help_text='Internal path to the interactive report. Example: /interactives/2019annualreport',
    )
    year = models.IntegerField(validators=[MinValueValidator(2005), MaxValueValidator(2050)])

    content_panels = FeatureablePageAbstract.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('year'),
            ],
            heading='General Information',
            classname='collapsible',
        ),
        MultiFieldPanel(
            [
                DocumentChooserPanel('report_english'),
                DocumentChooserPanel('report_french'),
                DocumentChooserPanel('report_financial'),
                FieldPanel('report_interactive'),
            ],
            heading='Reports',
            classname='collapsible',
        ),
        MultiFieldPanel(
            [
                ImageChooserPanel('image_poster'),
            ],
            heading='Images',
            classname='collapsible collapsed',
        )
    ]
    parent_page_types = ['core.AnnualReportListPage']
    subpage_types = []
    templates = 'core/annual_report_page.html'

    class Meta:
        verbose_name = 'Annual Report Page'
        verbose_name_plural = 'Annual Report Pages'
