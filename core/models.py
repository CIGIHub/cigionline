from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.forms.utils import flatatt
from django.utils.html import format_html, format_html_join
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtailmedia.blocks import AbstractMediaChooserBlock


class VideoBlock(AbstractMediaChooserBlock):
    def render_basic(self, value, context=None):
        if not value:
            return ''

        player_code = '''
        <div>
            <video width="320" height="240" controls>
                {0}
                Your browser does not support the video tag.
            </video>
        </div>
        '''

        return format_html(player_code, format_html_join(
            '\n', "<source{0}",
            [[flatatt(s)] for s in value.sources]
        ))


class HomePage(Page):
    """Singleton model for the home page."""

    max_count = 1
    subpage_types = [
        'articles.ArticleLandingPage',
        'articles.ArticleListPage',
        'careers.JobPostingListPage',
        'core.BasicPage',
        'events.EventListPage',
        'multimedia.MultimediaListPage',
        'multimedia.MultimediaSeriesListPage',
        'multimedia.MultimediaSeriesPage',
        'newsletters.NewsletterListPage',
        'people.PeoplePage',
        'people.PersonListPage',
        'publications.PublicationListPage',
        'publications.PublicationSeriesListPage',
        'research.ProjectListPage',
        'research.TopicListPage'
    ]
    templates = 'core/home_page.html'

    class Meta:
        verbose_name = 'Home Page'


class BasicPageAbstract(Page):
    """Page with subtitle."""

    # Body StreamField blocks
    body_default_blocks = [
        ('accordion', blocks.StructBlock([
            ('title', blocks.CharBlock(required=True)),
            ('text', blocks.RichTextBlock(required=True)),
            ('columns', blocks.ChoiceBlock(choices=[
                ('one', 'One'),
                ('two', 'Two'),
                ('three', 'Three'),
            ])),
        ])),
        ('autoplay_video', blocks.StructBlock([
            ('video', VideoBlock(required=False)),
            ('caption', blocks.CharBlock(required=False)),
        ])),
        ('chart', blocks.StructBlock([
            ('title', blocks.CharBlock(required=True)),
            ('image', ImageChooserBlock(required=True)),
            ('hide_image_caption', blocks.BooleanBlock(required=True)),
        ])),
        ('paragraph', blocks.RichTextBlock()),
        ('image', blocks.StructBlock([
            ('image', ImageChooserBlock(required=True)),
            ('hide_image_caption', blocks.BooleanBlock(required=True)),
        ])),
        ('image_full_bleed', blocks.StructBlock([
            ('image', ImageChooserBlock(required=True)),
            ('hide_image_caption', blocks.BooleanBlock(required=True)),
        ])),
        ('image_scroll', blocks.StructBlock([
            ('image', ImageChooserBlock(required=True)),
            ('hide_image_caption', blocks.BooleanBlock(required=True)),
        ])),
        ('block_quote', blocks.StructBlock([
            ('quote', blocks.RichTextBlock(required=True)),
            ('quote_author', blocks.CharBlock(required=False)),
            ('author_title', blocks.CharBlock(required=False)),
            ('image', ImageChooserBlock(required=False)),
            ('link_url', blocks.URLBlock(required=False)),
            ('link_text', blocks.CharBlock(required=False)),
        ])),
        ('embedded_multimedia', blocks.StructBlock([
            ('multimedia_url', blocks.URLBlock(required=True)),
            ('title', blocks.CharBlock(required=False)),
        ])),
        ('embedded_video', blocks.StructBlock([
            ('video_url', blocks.URLBlock(required=True)),
            ('caption', blocks.CharBlock(required=False)),
            ('image', ImageChooserBlock(required=False)),
            ('aspect_ratio', blocks.ChoiceBlock(choices=[
                ('landscape', 'Landscape'),
                ('square', 'Square'),
            ])),
        ])),
        ('external_quote', blocks.StructBlock([
            ('quote', blocks.RichTextBlock(required=True)),
            ('source', blocks.CharBlock(required=False)),
        ])),
        ('external_videos', blocks.ListBlock(blocks.StructBlock([
            ('title', blocks.CharBlock(required=True)),
            ('video_url', blocks.URLBlock(required=True)),
        ]))),
        ('highlight_title', blocks.CharBlock(required=True)),
        ('inline_video', blocks.PageChooserBlock(required=True, page_type='multimedia.MultimediaPage')),
        ('pull_quote_left', blocks.StructBlock([
            ('quote', blocks.RichTextBlock(required=True)),
            ('quote_author', blocks.CharBlock(required=False)),
            ('author_title', blocks.CharBlock(required=False)),
        ])),
        ('pull_quote_right', blocks.StructBlock([
            ('quote', blocks.RichTextBlock(required=True)),
            ('quote_author', blocks.CharBlock(required=False)),
            ('author_title', blocks.CharBlock(required=False)),
        ])),
        ('recommended', blocks.PageChooserBlock()),
        ('table', TableBlock()),
        ('text_background_block', blocks.RichTextBlock()),
        ('text_border_block', blocks.StructBlock([
            ('text', blocks.RichTextBlock(required=True)),
            ('border_colour', blocks.CharBlock(required=False)),
        ])),
        ('tool_tip', blocks.StructBlock([
            ('anchor', blocks.CharBlock(required=True)),
            ('text', blocks.RichTextBlock(required=True)),
            ('name', blocks.CharBlock(required=False)),
            ('title', blocks.CharBlock(required=False)),
            ('image', ImageChooserBlock(required=False)),
        ])),
    ]
    body_poster_block = [
        ('poster_block', blocks.PageChooserBlock(required=True, page_type='publications.PublicationPage')),
    ]

    body = StreamField(
        body_default_blocks,
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
    subtitle = RichTextField(blank=True, null=False, features=['bold', 'italic', 'link'])

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

    submenu_panel = MultiFieldPanel(
        [
            FieldPanel('submenu'),
        ],
        heading='Submenu',
        classname='collapsible collapsed',
    )
    settings_panels = Page.settings_panels + [
        submenu_panel,
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

    feature_panel = MultiFieldPanel(
        [
            FieldPanel('feature_title'),
            FieldPanel('feature_subtitle'),
            ImageChooserPanel('image_feature'),
        ],
        heading='Feature Information',
        classname='collapsible collapsed',
    )

    promote_panels = Page.promote_panels + [
        feature_panel,
    ]

    class Meta:
        abstract = True


class PublishablePageAbstract(Page):
    publishing_date = models.DateField()

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

    social_panel = MultiFieldPanel(
        [
            FieldPanel('social_title'),
            FieldPanel('social_description'),
            ImageChooserPanel('image_social'),
        ],
        heading='Social Media',
        classname='collapsible collapsed',
    )

    promote_panels = Page.promote_panels + [
        social_panel,
    ]

    class Meta:
        abstract = True


class ThemeablePageAbstract(Page):
    theme = models.ForeignKey(
        'core.Theme',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    theme_panel = MultiFieldPanel(
        [
            FieldPanel('theme'),
        ],
        heading='Theme',
        classname='collapsible collapsed',
    )
    settings_panels = Page.settings_panels + [
        theme_panel,
    ]

    class Meta:
        abstract = True


class FromTheArchivesPageAbstract(Page):
    from_the_archives = models.BooleanField(
        default=False,
        verbose_name='From the Archives',
        help_text='When enabled, show the "From the Archives" label if content is featured on front page.',
    )
    from_the_archives_blurb = RichTextField(
        blank=True,
        null=False,
        features=['bold', 'italic', 'link'],
        verbose_name='From the Archives Blurb',
        help_text='Block displayed on page.',
    )

    from_the_archives_panel = MultiFieldPanel(
        [
            FieldPanel('from_the_archives'),
            FieldPanel('from_the_archives_blurb'),
        ],
        heading='From the Archives',
        classname='collapsible collapsed',
    )

    content_panels = Page.content_panels + [
        from_the_archives_panel,
    ]

    class Meta:
        abstract = True


class ArchiveablePageAbstract(Page):
    class ArchiveStatus(models.IntegerChoices):
        UNARCHIVED = (0, 'No')
        ARCHIVED = (1, 'Yes')

    archive = models.IntegerField(choices=ArchiveStatus.choices, default=ArchiveStatus.UNARCHIVED)

    settings_panels = Page.settings_panels + [
        FieldPanel('archive'),
    ]

    class Meta:
        abstract = True


class BasicPage(
    BasicPageAbstract,
    FeatureablePageAbstract,
    ShareablePageAbstract,
):
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
    promote_panels = Page.promote_panels + [
        FeatureablePageAbstract.feature_panel,
        ShareablePageAbstract.social_panel,
    ]

    parent_page_types = ['core.BasicPage', 'core.HomePage']
    subpage_types = [
        'core.AnnualReportListPage',
        'core.BasicPage',
        'core.FundingPage',
        'people.PersonListPage',
        'research.ProjectPage',
    ]
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


class Theme(models.Model):
    name = models.CharField(max_length=255)

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_taxonomy_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name
