from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from streams.blocks import (
    AccordionBlock,
    ParagraphBlock,
    ReadMoreBlock,
    BlockQuoteBlock,
    ContactEmailBlock,
    ContactPersonBlock,
    EmbeddedVideoBlock,
    ExternalQuoteBlock,
    ImageBlock,
    AutoPlayVideoBlock,
    ImageFullBleedBlock,
    ChartBlock,
    PullQuoteLeftBlock,
    PullQuoteRightBlock,
    RecommendedBlock,
    TextBorderBlock,
    TweetBlock,
    InlineVideoBlock,
)
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
    StreamFieldPanel,
)
from wagtail.contrib.forms.models import (
    AbstractEmailForm,
    AbstractFormField,
)
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable, Page
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index


class BasicPageAbstract(models.Model):
    """Page with subtitle."""

    # Body StreamField blocks
    body_default_blocks = [
        ('block_quote', BlockQuoteBlock()),
        ('embedded_multimedia', blocks.StructBlock([
            ('multimedia_url', blocks.URLBlock(required=True)),
            ('title', blocks.CharBlock(required=False)),
        ])),
        ('embedded_video', EmbeddedVideoBlock()),
        ('image', ImageBlock()),
        ('inline_video', InlineVideoBlock(page_type='multimedia.MultimediaPage')),
        ('paragraph', ParagraphBlock()),
        ('table', TableBlock()),
        ('text_background_block', blocks.RichTextBlock(
            features=['bold', 'italic', 'link'],
        )),
    ]

    body_accordion_block = ('accordion', AccordionBlock())
    body_autoplay_video_block = ('autoplay_video', AutoPlayVideoBlock())
    body_chart_block = ('chart', ChartBlock())
    body_embedded_tiktok_block = ('embedded_tiktok', blocks.URLBlock(
        help_text='Paste the link to the video here. It should look like this: https://www.tiktok.com/@who/video/6805515697175792901',
        required=True,
    ))
    body_external_quote_block = ('external_quote', ExternalQuoteBlock())
    body_external_video_block = ('external_video', blocks.ListBlock(blocks.StructBlock([
        ('title', blocks.CharBlock(required=True)),
        ('video_url', blocks.URLBlock(required=True)),
    ])))
    body_highlight_title_block = ('highlight_title', blocks.CharBlock(required=True))
    body_image_full_bleed_block = ('image_full_bleed', ImageFullBleedBlock())
    body_image_scroll_block = ('image_scroll', blocks.StructBlock([
        ('image', ImageChooserBlock(required=True)),
        ('hide_image_caption', blocks.BooleanBlock(required=False)),
    ]))
    body_poster_block = ('poster_block', blocks.PageChooserBlock(required=True, page_type='publications.PublicationPage'))
    body_pull_quote_left_block = ('pull_quote_left', PullQuoteLeftBlock())
    body_pull_quote_right_block = ('pull_quote_right', PullQuoteRightBlock())
    body_read_more_block = ('read_more', ReadMoreBlock())
    body_recommended_block = ('recommended', RecommendedBlock())
    body_text_border_block = ('text_border_block', TextBorderBlock())
    body_tool_tip_block = ('tool_tip', blocks.StructBlock([
        ('anchor', blocks.CharBlock(required=True)),
        ('text', blocks.RichTextBlock(
            features=['bold', 'italic', 'link'],
            required=True,
        )),
        ('name', blocks.CharBlock(required=False)),
        ('title', blocks.CharBlock(required=False)),
        ('image', ImageChooserBlock(required=False)),
    ]))
    body_tweet_block = ('tweet', TweetBlock())

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
    submenu_panel = MultiFieldPanel(
        [
            FieldPanel('submenu'),
        ],
        heading='Submenu',
        classname='collapsible collapsed',
    )

    search_fields = [
        index.SearchField('body'),
        index.SearchField('subtitle'),
    ]

    class Meta:
        abstract = True


class FeatureablePageAbstract(models.Model):
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

    class Meta:
        abstract = True


class SearchablePageAbstract(models.Model):
    search_terms = StreamField(
        [
            ('search_term', blocks.CharBlock()),
        ],
        blank=True,
        help_text='A list of search terms for which this page will be elevated in the search results.',
    )

    search_panel = MultiFieldPanel(
        [
            StreamFieldPanel('search_terms'),
        ],
        heading='Search Terms',
        classname='collapsible collapsed',
    )

    class Meta:
        abstract = True


class ShareablePageAbstract(models.Model):
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

    class Meta:
        abstract = True


class ThemeablePageAbstract(models.Model):
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

    def get_theme_dir(self):
        if self.theme:
            return self.theme.name.lower().replace(' ', '_').replace("-", '_')
        return ''

    class Meta:
        abstract = True


class FromTheArchivesPageAbstract(models.Model):
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

    class Meta:
        abstract = True


class ArchiveablePageAbstract(models.Model):
    class ArchiveStatus(models.IntegerChoices):
        UNARCHIVED = (0, 'No')
        ARCHIVED = (1, 'Yes')

    archive = models.IntegerField(choices=ArchiveStatus.choices, default=ArchiveStatus.UNARCHIVED)

    archive_panel = MultiFieldPanel(
        [
            FieldPanel('archive'),
        ],
        heading='Archive',
        classname='collapsible collapsed',
    )

    class Meta:
        abstract = True


class ContentPage(Page, SearchablePageAbstract):
    publishing_date = models.DateTimeField(blank=False, null=True)
    topics = ParentalManyToManyField('research.TopicPage', blank=True)

    recommended_panel = MultiFieldPanel(
        [
            InlinePanel('recommended'),
        ],
        heading='Recommended',
        classname='collapsible collapsed',
    )

    content_panels = Page.content_panels + [
        FieldPanel('publishing_date'),
        FieldPanel('topics'),
    ]

    search_fields = [
        index.FilterField('topicpage_id'),
    ]

    def on_form_bound(self):
        self.bound_field = self.form[self.field_name]
        heading = self.heading or self.bound_field.label
        help_text = self.help_text or self.bound_field.help_text

        self.heading = heading
        self.bound_field.label = heading
        self.help_text = help_text
        self.bound_field.help_text = help_text


class ContentPageRecommendedContent(Orderable):
    content_page = ParentalKey(
        'core.ContentPage',
        related_name='recommended',
    )
    recommended_content_page = models.ForeignKey(
        'wagtailcore.Page',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Recommended Content',
    )

    panels = [
        PageChooserPanel(
            'recommended_content_page',
            ['wagtailcore.Page'],
        )
    ]


class BasicPage(
    Page,
    BasicPageAbstract,
    FeatureablePageAbstract,
    SearchablePageAbstract,
    ShareablePageAbstract,
):
    """Page with StreamField body"""

    related_files = StreamField(
        [
            ('file', DocumentChooserBlock()),
        ],
        blank=True,
    )

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
        BasicPageAbstract.images_panel,
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
        SearchablePageAbstract.search_panel,
    ]

    parent_page_types = ['careers.JobPostingListPage', 'core.BasicPage', 'home.HomePage']
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


class FundingPage(BasicPageAbstract, Page):
    """
    A special singleton page for /about/funding that contains a hardcoded
    table with the funding details.
    """

    max_count = 1
    parent_page_types = ['core.BasicPage']
    subpage_types = []
    templates = 'core/funding_page.html'

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
        BasicPageAbstract.images_panel,
    ]
    settings_panels = Page.settings_panels + [
        BasicPageAbstract.submenu_panel,
    ]

    class Meta:
        verbose_name = 'Funding Page'


class AnnualReportListPage(BasicPageAbstract, Page):
    max_count = 1
    parent_page_types = ['core.BasicPage']
    subpage_types = ['core.AnnualReportPage']
    templates = 'core/annual_report_list_page.html'

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
        BasicPageAbstract.images_panel,
    ]
    settings_panels = Page.settings_panels + [
        BasicPageAbstract.submenu_panel,
    ]

    class Meta:
        verbose_name = 'Annual Report List Page'


class AnnualReportPage(FeatureablePageAbstract, Page, SearchablePageAbstract):
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

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_node_id = models.IntegerField(blank=True, null=True)

    content_panels = Page.content_panels + [
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
    promote_panels = Page.promote_panels + [
        FeatureablePageAbstract.feature_panel,
        SearchablePageAbstract.search_panel,
    ]
    parent_page_types = ['core.AnnualReportListPage']
    subpage_types = []
    templates = 'core/annual_report_page.html'

    class Meta:
        verbose_name = 'Annual Report Page'
        verbose_name_plural = 'Annual Report Pages'


class PrivacyNoticePage(
    Page,
    BasicPageAbstract,
):
    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
    ]

    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = []
    template = 'core/privacy_notice_page.html'

    class Meta:
        verbose_name = 'Privacy Notice'


class Theme(models.Model):
    name = models.CharField(max_length=255)

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_taxonomy_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name


class ContactFormField(AbstractFormField):
    page = ParentalKey(
        'core.ContactPage',
        on_delete=models.CASCADE,
        related_name='form_fields',
    )


class ContactPage(AbstractEmailForm):
    events_contact = StreamField(
        [
            ('contact_email', ContactEmailBlock()),
            ('contact_person', ContactPersonBlock(
                page_type='people.PersonPage',
            )),
        ],
        blank=True,
    )
    human_resources_contact = StreamField(
        [
            ('contact_email', ContactEmailBlock()),
            ('contact_person', ContactPersonBlock(
                page_type='people.PersonPage',
            )),
        ],
        blank=True,
    )
    media_contact = StreamField(
        [
            ('contact_email', ContactEmailBlock()),
            ('contact_person', ContactPersonBlock(
                page_type='people.PersonPage',
            )),
        ],
        blank=True,
    )
    thank_you_message = RichTextField(
        blank=True,
        null=False,
        features=['bold', 'italic', 'link'],
    )

    content_panels = AbstractEmailForm.content_panels + [
        InlinePanel('form_fields', label='Form Fields'),
        FieldPanel('thank_you_message'),
        MultiFieldPanel(
            [
                FieldPanel('from_address'),
                FieldPanel('to_address'),
                FieldPanel('subject'),
            ],
            heading='Email Settings',
        ),
        MultiFieldPanel(
            [
                StreamFieldPanel('human_resources_contact'),
            ],
            heading='Human Resources',
        ),
        MultiFieldPanel(
            [
                StreamFieldPanel('events_contact'),
            ],
            heading='Events',
        ),
        MultiFieldPanel(
            [
                StreamFieldPanel('media_contact'),
            ],
            heading='Media',
        ),
    ]

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        for name, field in form.fields.items():
            placeholder = field.help_text
            if field.required:
                placeholder = placeholder + '*'
            field.widget.attrs.update({'placeholder': placeholder})
        return form

    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = []
    template = 'core/contact_page.html'
    landing_page_template = 'core/contact_page_landing.html'

    class Meta:
        verbose_name = 'Contact Page'
