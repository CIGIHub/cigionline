from django.db import models
from django.utils.functional import cached_property
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from search.filters import (
    # AuthorFilterField,
    ParentalManyToManyFilterField,
)
from streams.blocks import (
    AccordionBlock,
    ParagraphBlock,
    ReadMoreBlock,
    BlockQuoteBlock,
    EmbeddedMultimediaBlock,
    EmbeddedVideoBlock,
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
    TableStreamBlock,
    TextBackgroundBlock,
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
        ('table', TableStreamBlock()),
        ('text_background_block', TextBackgroundBlock(
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
        index.FilterField('archive'),
    ]

    class Meta:
        abstract = True


class ContentPage(Page, SearchablePageAbstract):
    projects = ParentalManyToManyField('research.ProjectPage', blank=True, related_name='content_pages')
    publishing_date = models.DateTimeField(blank=False, null=True)
    topics = ParentalManyToManyField('research.TopicPage', blank=True, related_name='content_pages')

    @property
    def topics_sorted(self):
        return self.topics.order_by('title')

    @property
    def author_ids(self):
        return [item.author.id for item in self.authors.all()]

    @property
    def author_names(self):
        return [item.author.title for item in self.authors.all()]

    @property
    def related_people_ids(self):
        people_ids = []
        for author in self.authors.all():
            people_ids.append(author.author.id)
        for editor in self.editors.all():
            people_ids.append(editor.editor.id)
        if hasattr(self.specific, 'cigi_people_mentioned'):
            for block in self.specific.cigi_people_mentioned:
                if block.block_type == 'cigi_person':
                    people_ids.append(block.value)
        return people_ids

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
        return self.authors.count()

    def get_recommended(self):
        recommended_page_ids = self.recommended.values_list('recommended_content_page_id', flat=True)[:3]
        pages = Page.objects.specific().prefetch_related(
            'authors__author',
            'topics',
        ).in_bulk(recommended_page_ids)
        return [pages[x] for x in recommended_page_ids]

    @cached_property
    def recommended_content(self):
        recommended_content = self.get_recommended()
        exclude_ids = [self.id]
        exclude_ids += [item.id for item in recommended_content]

        additional_content = list(ContentPage.objects.specific().live().public().filter(
            topics__in=self.topics.values_list('id', flat=True),
            publishing_date__isnull=False,
            eventpage__isnull=True
        ).exclude(id__in=exclude_ids).exclude(
            articlepage__article_type__title='CIGI in the News'
        ).prefetch_related('authors__author', 'topics').order_by('-publishing_date', 'topics')[:12 - len(recommended_content)])

        recommended_content = list(recommended_content) + additional_content

        return recommended_content

    authors_panel = MultiFieldPanel(
        [
            InlinePanel('authors'),
        ],
        heading='Authors',
        classname='collapsible collapsed',
    )
    editors_panel = MultiFieldPanel(
        [
            InlinePanel('editors'),
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

    content_panels = [
        FieldPanel('publishing_date'),
        FieldPanel('topics'),
    ]

    search_fields = Page.search_fields + [
        index.FilterField('author_ids'),
        index.SearchField('author_names'),
        index.FilterField('contenttype'),
        index.FilterField('contentsubtype'),
        ParentalManyToManyFilterField('projects'),
        index.FilterField('publishing_date'),
        index.FilterField('related_people_ids'),
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
    hide_link = models.BooleanField(default=False)

    panels = [
        PageChooserPanel(
            'author',
            ['people.PersonPage'],
        ),
        FieldPanel('hide_link'),
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
    hide_link = models.BooleanField(default=False)

    panels = [
        PageChooserPanel(
            'editor',
            ['people.PersonPage'],
        ),
        FieldPanel('hide_link'),
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
    ThemeablePageAbstract,
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
                InlinePanel(
                    'featured_pages',
                    max_num=9,
                    min_num=0,
                    label='Page',
                ),
            ],
            heading='Featured Content',
            classname='collapsible collapsed',
        ),
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
    settings_panels = Page.settings_panels + [
        ThemeablePageAbstract.theme_panel,
    ]

    search_fields = Page.search_fields + BasicPageAbstract.search_fields

    parent_page_types = ['careers.JobPostingListPage', 'core.BasicPage', 'home.HomePage']
    subpage_types = [
        'annual_reports.AnnualReportListPage',
        'core.BasicPage',
        'core.FundingPage',
        'people.PersonListPage',
        'research.ProjectPage',
    ]
    template = 'core/basic_page.html'

    def get_featured_pages(self):
        featured_page_ids = self.featured_pages.order_by('sort_order').values_list('featured_page', flat=True)
        pages = Page.objects.specific().prefetch_related(
            'authors__author',
            'topics',
        ).in_bulk(featured_page_ids)
        return [pages[x] for x in featured_page_ids]

    def get_template(self, request, *args, **kwargs):
        standard_template = super(BasicPage, self).get_template(request, *args, **kwargs)
        if self.theme:
            return f'themes/{self.get_theme_dir()}/basic_page.html'
        return standard_template

    def get_context(self, request):
        context = super().get_context(request)

        context['featured_pages'] = self.get_featured_pages()

    class Meta:
        verbose_name = 'Page'
        verbose_name_plural = 'Pages'


class BasicPageFeaturedPage(Orderable):
    basic_page = ParentalKey(
        'core.BasicPage',
        related_name='featured_pages',
    )
    featured_page = models.ForeignKey(
        'wagtailcore.Page',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Page',
    )

    panels = [
        PageChooserPanel(
            'featured_page',
            ['wagtailcore.Page'],
        ),
    ]


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

    search_fields = Page.search_fields + BasicPageAbstract.search_fields

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

    search_fields = Page.search_fields + BasicPageAbstract.search_fields

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
