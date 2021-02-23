from django.db import models
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from search.filters import AuthorFilterField, ParentalManyToManyFilterField
from streams.blocks import (
    AccordionBlock,
    ParagraphBlock,
    ReadMoreBlock,
    BlockQuoteBlock,
    EmbeddedMultimediaBlock,
    EmbeddedVideoBlock,
    ExternalPersonBlock,
    ExternalQuoteBlock,
    ExternalVideoBlock,
    HeroLinkBlock,
    HeroDocumentBlock,
    ImageBlock,
    ImageScrollBlock,
    AutoPlayVideoBlock,
    ImageFullBleedBlock,
    ChartBlock,
    PosterBlock,
    PullQuoteLeftBlock,
    PullQuoteRightBlock,
    RecommendedBlock,
    TextBorderBlock,
    TooltipBlock,
    TweetBlock,
    InlineVideoBlock,
    HighlightTitleBlock,
)
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
    StreamFieldPanel,
)
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable, Page
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index


class BasicPageAbstract(models.Model):
    """Page with subtitle."""

    # Body StreamField blocks
    body_default_blocks = [
        ('block_quote', BlockQuoteBlock()),
        ('embedded_multimedia', EmbeddedMultimediaBlock()),
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
    body_external_video_block = ('external_video', ExternalVideoBlock())
    body_highlight_title_block = ('highlight_title', HighlightTitleBlock())
    body_image_full_bleed_block = ('image_full_bleed', ImageFullBleedBlock())
    body_image_scroll_block = ('image_scroll', ImageScrollBlock())
    body_poster_block = ('poster_block', PosterBlock(required=True, page_type='publications.PublicationPage'))
    body_pull_quote_left_block = ('pull_quote_left', PullQuoteLeftBlock())
    body_pull_quote_right_block = ('pull_quote_right', PullQuoteRightBlock())
    body_read_more_block = ('read_more', ReadMoreBlock())
    body_recommended_block = ('recommended', RecommendedBlock())
    body_text_border_block = ('text_border_block', TextBorderBlock())
    body_tool_tip_block = ('tool_tip', TooltipBlock())
    body_tweet_block = ('tweet', TweetBlock())

    body = StreamField(
        body_default_blocks,
        blank=True,
    )
    hero_link = StreamField(
        [
            ('hero_link', HeroLinkBlock()),
            ('hero_document', HeroDocumentBlock()),
        ],
        blank=True,
        help_text='Text with link to url, email or document and optional icon that appears below the page title in the hero section.',
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

    @property
    def image_hero_url(self):
        if self.image_hero:
            return self.image_hero.get_rendition('fill-520x390').url
        return ''

    # Override content_panels to put the title panel within a MultiFieldPanel
    title_panel = MultiFieldPanel(
        [
            FieldPanel('title'),
            FieldPanel('subtitle'),
        ],
        heading='Title',
        classname='collapsible'
    )
    hero_link_panel = MultiFieldPanel(
        [
            StreamFieldPanel('hero_link'),
        ],
        heading='Hero Link',
        classname='collapsible collapsed'
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

    search_fields = [
        index.SearchField('archive'),
    ]

    class Meta:
        abstract = True


class ContentPage(Page, SearchablePageAbstract):
    external_authors = StreamField(
        [
            ('external_person', ExternalPersonBlock()),
        ],
        blank=True,
    )
    external_editors = StreamField(
        [
            ('external_person', ExternalPersonBlock()),
        ],
        blank=True,
    )
    projects = ParentalManyToManyField('research.ProjectPage', blank=True)
    publishing_date = models.DateTimeField(blank=False, null=True)
    topics = ParentalManyToManyField('research.TopicPage', blank=True)

    @property
    def contenttype(self):
        if self.specific and hasattr(self.specific, '_meta') and hasattr(self.specific._meta, 'verbose_name'):
            contenttype = self.specific._meta.verbose_name
            return contenttype
        return ''

    @property
    def contentsubtype(self):
        if self.specific and hasattr(self.specific, '_meta') and hasattr(self.specific._meta, 'verbose_name'):
            contenttype = self.specific._meta.verbose_name
            if contenttype == 'Opinion':
                return self.specific.article_type.title
            if contenttype == 'Publication':
                return self.specific.publication_type.title
            if contenttype == 'Multimedia':
                return self.specific.get_multimedia_type_display()
            return contenttype
        return ''

    @property
    def pdf_download(self):
        if self.specific and hasattr(self.specific, '_meta') and self.specific._meta.verbose_name == 'Publication' and len(self.specific.pdf_downloads) > 0:
            return self.specific.pdf_downloads[0].value['file'].url
        return ''

    def author_count(self):
        # @todo test this
        return self.authors.count() + len(self.external_authors)

    def recommended_content(self):
        recommended_content = []
        topic_content = []
        for item in self.recommended.all()[:3]:
            recommended_content.append(item.recommended_content_page.specific)
        for topic in self.topics.all():
            topic_content.append(
                ContentPage
                .objects
                .live()
                .public()
                .filter(topics=topic, publishing_date__isnull=False, eventpage__isnull=True)
                .exclude(id=self.id)
                .exclude(articlepage__article_type__title='CIGI in the News')
                .order_by('-publishing_date')
            )
        for i in range(10):
            for topic in topic_content:
                if topic[i] in recommended_content:
                    continue
                recommended_content.append(topic[i])
                if len(recommended_content) == 12:
                    return recommended_content
        return recommended_content

    authors_panel = MultiFieldPanel(
        [
            InlinePanel('authors'),
            StreamFieldPanel('external_authors'),
        ],
        heading='Authors',
        classname='collapsible collapsed',
    )
    editors_panel = MultiFieldPanel(
        [
            InlinePanel('editors'),
            StreamFieldPanel('external_editors'),
        ],
        heading='Editors',
        classname='collapsible collapsed',
    )
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
        AuthorFilterField('authors'),
        index.FilterField('contenttype'),
        index.FilterField('contentsubtype'),
        ParentalManyToManyFilterField('projects'),
        index.FilterField('publishing_date'),
        ParentalManyToManyFilterField('topics'),
    ]

    def on_form_bound(self):
        self.bound_field = self.form[self.field_name]
        heading = self.heading or self.bound_field.label
        help_text = self.help_text or self.bound_field.help_text

        self.heading = heading
        self.bound_field.label = heading
        self.help_text = help_text
        self.bound_field.help_text = help_text


class ContentPageAuthor(Orderable):
    content_page = ParentalKey(
        'core.ContentPage',
        related_name='authors',
    )
    author = models.ForeignKey(
        'people.PersonPage',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='content_pages_as_author',
        verbose_name='Author',
    )

    panels = [
        PageChooserPanel(
            'author',
            ['people.PersonPage'],
        ),
    ]


class ContentPageEditor(Orderable):
    content_page = ParentalKey(
        'core.ContentPage',
        related_name='editors',
    )
    editor = models.ForeignKey(
        'people.PersonPage',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='content_pages_as_editor',
        verbose_name='Editor',
    )

    panels = [
        PageChooserPanel(
            'editor',
            ['people.PersonPage'],
        ),
    ]


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
        'annual_reports.AnnualReportListPage',
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
