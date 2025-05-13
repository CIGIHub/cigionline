from bs4 import BeautifulSoup
from django.conf import settings
from django.db import models
from django.db.models.fields import CharField
from django.http import JsonResponse
from django.http.response import Http404
from django.utils.functional import cached_property
from django.shortcuts import render
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from search.filters import (
    # AuthorFilterField,
    ParentalManyToManyFilterField,
)
from streams.blocks import (
    AccordionBlock,
    AdditionalDisclaimerBlock,
    AdditionalImageBlock,
    AddtionalPagesBlock,
    ExtractBlock,
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
    PersonsListBlock,
    PublicastionsListBlock,
    PosterBlock,
    PullQuoteLeftBlock,
    PullQuoteRightBlock,
    RecommendedBlock,
    SliderGalleryBlock,
    TableStreamBlock,
    TextBackgroundBlock,
    TextBorderBlock,
    TimelineGalleryBlock,
    TooltipBlock,
    TweetBlock,
    InlineVideoBlock,
    HighlightTitleBlock,
    LineBreakBlock,
    FilesBlock,
)
from uploads.models import DocumentUpload
from utils.email_utils import send_email, extract_errors_as_string
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
    TitleFieldPanel,
)
from wagtail import blocks
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page, Collection
from wagtail.url_routing import RouteResult
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.documents.models import Document
from wagtail.images.blocks import ImageChooserBlock
from wagtail.search import index
from wagtail.admin.forms import WagtailAdminPageForm
from .forms import Think7AbstractUploadForm
import math


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
        ('slider_gallery', SliderGalleryBlock()),
        ('table', TableStreamBlock()),
        ('text_background_block', TextBackgroundBlock(
            features=['bold', 'italic', 'link'],
        )),
        ('persons_list_block', PersonsListBlock()),
        ('publications_list_block', PublicastionsListBlock()),
        ('additional_pages_block', AddtionalPagesBlock()),
        ('files_block', FilesBlock()),
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
    body_extract_block = ('extract', ExtractBlock())
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
    additional_image_block = ('additional_image', AdditionalImageBlock())
    additional_disclaimer_block = ('additional_disclaimer', AdditionalDisclaimerBlock())
    line_break_block = ('linebreak', LineBreakBlock())

    body = StreamField(
        body_default_blocks,
        blank=True,
        use_json_field=True,
    )
    hero_link = StreamField(
        [
            ('hero_link', HeroLinkBlock()),
            ('hero_document', HeroDocumentBlock()),
        ],
        blank=True,
        help_text='Text with link to url, email or document and optional icon that appears below the page title in the hero section.',
        use_json_field=True,
    )
    image_hero = models.ForeignKey(
        'images.CigionlineImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Hero Image',
        help_text='A large image to be displayed prominently on the page.',
    )
    image_banner = models.ForeignKey(
        'images.CigionlineImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Banner Image',
        help_text='A banner image to be displayed as background of the hero section.',
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
    def body_snippet(self):
        snippet = ''
        for i in range(5):
            try:
                snippet = BeautifulSoup(self.body[i].value.source, "html.parser").get_text()
                break
            except AttributeError:
                continue
            except IndexError:
                break
        if self.body:
            return snippet[:350] if len(snippet) > 350 else snippet
        else:
            return snippet

    @property
    def image_hero_url(self):
        if self.specific.image_feature:
            return self.specific.image_feature.get_rendition('fill-520x390').url
        if self.image_hero:
            return self.image_hero.get_rendition('fill-520x390').url
        return ''

    @property
    def word_count(self):
        count = 0
        for block in self.body:
            if block.block_type == 'paragraph':
                count += len(str(block.value).split())
        return count

    @property
    def read_time(self):
        read_time = 1
        if self.word_count > 0:
            read_time = int(math.ceil(self.word_count / 325))
        return read_time

    @property
    def has_publications_list_block(self):
        for block in self.body:
            if block.block_type == 'publications_list_block':
                return True
        return False

    # Override content_panels to put the title panel within a MultiFieldPanel
    title_panel = MultiFieldPanel(
        [
            TitleFieldPanel('title'),
            FieldPanel('subtitle'),
        ],
        heading='Title',
        classname='collapsible'
    )
    hero_link_panel = MultiFieldPanel(
        [
            FieldPanel('hero_link'),
        ],
        heading='Hero Link',
        classname='collapsible collapsed'
    )
    body_panel = MultiFieldPanel(
        [
            FieldPanel('body'),
        ],
        heading='Body',
        classname='collapsible collapsed'
    )
    images_panel = MultiFieldPanel(
        [
            FieldPanel('image_hero'),
            FieldPanel('image_banner'),
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
    feature_subtitle = models.CharField(blank=True, max_length=500)
    feature_title = models.CharField(blank=True, max_length=255)
    image_feature = models.ForeignKey(
        'images.CigionlineImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Feature image',
        help_text='Image used when featuring on landing pages such as the home page',
    )
    feature_url = models.URLField(blank=True)

    feature_panel = MultiFieldPanel(
        [
            FieldPanel('feature_title'),
            FieldPanel('feature_subtitle'),
            FieldPanel('image_feature'),
            FieldPanel('feature_url'),
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
        use_json_field=True,
    )
    search_result_description = models.CharField(
        blank=True,
        null=True,
        max_length=1024,
        help_text='Text that is displayed when this page appears in search results')
    exclude_from_search = models.BooleanField(default=False)

    search_panel = MultiFieldPanel(
        [
            FieldPanel('search_terms'),
            FieldPanel('search_result_description'),
            FieldPanel('exclude_from_search'),
        ],
        heading='Search',
        classname='collapsible collapsed',
    )

    search_fields = [
        index.SearchField('search_terms'),
        index.FilterField('exclude_from_search'),
    ]

    class Meta:
        abstract = True


class ShareablePageAbstract(models.Model):
    social_title = models.CharField(blank=True, max_length=255)
    social_description = models.CharField(blank=True, max_length=255)
    image_social = models.ForeignKey(
        'images.CigionlineImage',
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
            FieldPanel('image_social'),
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


class ContentPageForm(WagtailAdminPageForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from research.models import TopicPage, CountryPage

        # filter out archived topics
        self.fields['topics'].queryset = TopicPage.objects.filter(archive=0)

        # order commonly used country tags first
        common_countries = [
            'Canada',
            'United States of America',
            'Russian Federation',
            'China',
            'India',
            'Brazil',
        ]

        _whens = []
        for sort_index, value in enumerate(common_countries):
            _whens.append(models.When(title=value, then=sort_index))

        self.fields['countries'].queryset = CountryPage.objects.filter(archive=0).annotate(
            _sort_index=models.Case(
                *_whens,
                output_field=models.IntegerField()
            )
        ).order_by('_sort_index', 'title')


class ContentPage(Page, SearchablePageAbstract):
    projects = ParentalManyToManyField('research.ProjectPage', blank=True, related_name='content_pages')
    publishing_date = models.DateTimeField(blank=False, null=True)
    topics = ParentalManyToManyField('research.TopicPage', blank=True, related_name='content_pages')
    countries = ParentalManyToManyField('research.CountryPage', blank=True, related_name='content_pages')

    @property
    def topics_sorted(self):
        return self.topics.order_by('title')

    @property
    def topic_names(self):
        return [item.title for item in self.topics.all()]

    @property
    def country_names(self):
        return [item.title for item in self.countries.all()]

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
        if self.specific and hasattr(self.specific, 'cigi_people_mentioned'):
            for person in self.cigi_people_mentioned.all():
                people_ids.append(person.person.id)
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
            if contenttype == 'Event':
                return self.specific.get_event_type_display()
            return contenttype
        return ''

    @property
    def pdf_download(self):
        if self.specific and hasattr(self.specific, '_meta') and self.specific._meta.verbose_name == 'Publication' and len(self.specific.pdf_downloads) > 0:
            return self.specific.pdf_downloads[0].value['file'].url
        return ''

    @cached_property
    def author_count(self):
        # @todo test this
        return self.authors.count()

    @cached_property
    def editor_count(self):
        return self.editors.count()

    def get_recommended(self):
        recommended_page_ids = self.recommended.values_list('recommended_content_page_id', flat=True)[:3]
        pages = Page.objects.specific().select_related(
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
        ).exclude(
            id__in=exclude_ids
        ).exclude(
            articlepage__article_type__title='CIGI in the News'
        ).exclude(
            publicationpage__publication_type__title='Working Paper'
        ).exclude(
            path__startswith='00010002'
        ).prefetch_related('authors__author', 'topics').distinct().order_by('-publishing_date')[:12 - len(recommended_content)])

        recommended_content = list(recommended_content) + additional_content

        return recommended_content

    @cached_property
    def recommended_content_preview(self):
        recommended_pages = [page.recommended_content_page.specific for page in self.recommended.all()[:3]]

        exclude_ids = [self.id]
        exclude_ids += [item.id for item in recommended_pages]

        additional_content = list(ContentPage.objects.specific().live().public().filter(
            topics__in=self.topics.values_list('id', flat=True),
            publishing_date__isnull=False,
            eventpage__isnull=True
        ).exclude(id__in=exclude_ids).exclude(
            articlepage__article_type__title='CIGI in the News'
        ).prefetch_related('authors__author', 'topics').distinct().order_by('-publishing_date')[:12 - len(recommended_pages)])

        recommended_content = list(recommended_pages) + additional_content

        return recommended_content

    def page_cache_key(self):
        series = f'S:{self.specific.article_series.id}' if self.specific and self.specific.article_series else ''
        return f'Ct:{self.specific.contenttype}Cst:{self.specific.contentsubtype}Id:{self.id}{series}'

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
        FieldPanel('countries'),
    ]

    base_form_class = ContentPageForm

    search_fields = Page.search_fields + SearchablePageAbstract.search_fields + [
        index.FilterField('author_ids'),
        index.SearchField('author_names', boost=2),
        index.FilterField('author_names'),
        index.FilterField('contenttype'),
        index.FilterField('contentsubtype'),
        ParentalManyToManyFilterField('projects'),
        index.FilterField('publishing_date'),
        index.SearchField('topic_names'),
        index.FilterField('related_people_ids'),
        ParentalManyToManyFilterField('topics'),
        index.SearchField('country_names'),
        ParentalManyToManyFilterField('countries'),
    ]

    def on_form_bound(self):
        self.bound_field = self.form[self.field_name]
        heading = self.heading or self.bound_field.label
        help_text = self.help_text or self.bound_field.help_text

        self.heading = heading
        self.bound_field.label = heading
        self.help_text = help_text
        self.bound_field.help_text = help_text

    class Meta:
        indexes = [
            models.Index(fields=['publishing_date'])
        ]


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
        use_json_field=True,
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
                FieldPanel('related_files'),
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
        BasicPageAbstract.submenu_panel,
        ThemeablePageAbstract.theme_panel,
    ]

    search_fields = Page.search_fields + BasicPageAbstract.search_fields + SearchablePageAbstract.search_fields

    parent_page_types = ['careers.JobPostingListPage', 'core.BasicPage', 'home.HomePage', 'home.Think7HomePage']
    subpage_types = [
        'annual_reports.AnnualReportListPage',
        'core.BasicPage',
        'core.FundingPage',
        'core.TwentiethPage',
        'core.TwentiethPageSingleton',
        'people.PersonListPage',
        'research.ProjectPage',
    ]
    template = 'core/basic_page.html'

    def get_featured_pages(self):
        featured_page_ids = self.featured_pages.order_by('sort_order').values_list('featured_page', flat=True)
        pages = Page.objects.specific().in_bulk(featured_page_ids)
        return [pages[x] for x in featured_page_ids]

    def get_template(self, request, *args, **kwargs):
        standard_template = super(BasicPage, self).get_template(request, *args, **kwargs)
        if self.theme:
            return f'themes/{self.get_theme_dir()}/basic_page.html'
        return standard_template

    def get_context(self, request):
        context = super().get_context(request)

        context['featured_pages'] = self.get_featured_pages()
        return context

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
    SearchablePageAbstract,
):
    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
    ]

    search_fields = Page.search_fields + BasicPageAbstract.search_fields + SearchablePageAbstract.search_fields

    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = []
    template = 'core/privacy_notice_page.html'

    class Meta:
        verbose_name = 'Privacy Notice'


class TwentiethPage(
    Page,
    BasicPageAbstract,
    FeatureablePageAbstract,
    SearchablePageAbstract,
    ShareablePageAbstract,
):

    def slides_json(self):
        slides = []
        counter = 1
        for item in self.slides.all():
            body = []
            slide = item.slide
            for block in slide.body:
                if block.block_type == 'text':
                    body.append({'type': 'text', 'value': block.value.source})
                elif block.block_type == 'separator':
                    body.append({'type': 'separator', 'value': None})
                elif block.block_type == 'video':
                    body.append({
                        'type': 'video',
                        'value': {
                            'video_url': block.value['video_url'],
                            'video_image': block.value['video_image'].get_rendition('original').url if block.value['video_image'] else '',
                        }})
                else:
                    body.append({'type': block.block_type, 'value': block.value})
            slide_data = {
                'title': slide.title_override if slide.title_override else slide.title,
                'body': body,
                'background': slide.image_background.get_rendition('original').url if slide.image_background else '',
                'background_colour': slide.background_colour,
                'timeline': [{
                    'year': year.value['year'],
                    'body': year.value['text'].source,
                    'image': year.value['image'].get_rendition('original').url if year.value['image'] else '',
                    'video': {
                        'video_url': year.value['video_url'] if year.value['video_url'] else '',
                        'video_image': year.value['video_image'].get_rendition('original').url if year.value['video_image'] else '',
                    }
                } for year in slide.timeline],
                'theme': slide.theme,
                'slug': slide.slug,
                'slide_number': counter,
                'walls_embed': slide.walls_embed,
            }
            slide_data['prev_slide'] = counter - 1 if counter > 1 else None
            slide_data['next_slide'] = counter + 1 if counter < len(self.slides.all()) else None
            slides.append(slide_data)
            counter = counter + 1

        return slides

    def route(self, request, path_components):
        if path_components:
            # request is for a child of this page
            child_slug = path_components[0]

            # find a matching child or 404
            try:
                self.get_children().get(slug=child_slug)
            except Page.DoesNotExist:
                raise Http404

        if self.live:
            # Return a RouteResult that will tell Wagtail to call
            # this page's serve() method
            return RouteResult(self, kwargs={'path_components': path_components})
        else:
            # the page matches the request, but isn't published, so 404
            raise Http404

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        if kwargs.get('path_components'):
            context['initial_slide'] = kwargs.get('path_components')[0]

        return context

    content_panels = [
        BasicPageAbstract.title_panel,
        MultiFieldPanel(
            [
                InlinePanel('slides'),
            ],
            heading='slides',
            classname='collapsible',
        )
    ]

    promote_panels = Page.promote_panels + [
        FeatureablePageAbstract.feature_panel,
        ShareablePageAbstract.social_panel,
        SearchablePageAbstract.search_panel,
    ]
    settings_panels = Page.settings_panels + [
        BasicPageAbstract.submenu_panel,
    ]

    search_fields = Page.search_fields + BasicPageAbstract.search_fields + SearchablePageAbstract.search_fields

    max_count = 1
    parent_page_types = ['core.BasicPage']
    subpage_types = ['core.SlidePage']
    templates = 'core/twentieth_page.html'

    class Meta:
        verbose_name = 'Twentieth Page'


class TwentiethPageSlide(Orderable):
    twentieth_page = ParentalKey(
        'core.TwentiethPage',
        related_name='slides',
    )
    slide = models.ForeignKey(
        'core.SlidePage',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Slide',
    )

    panels = [
        PageChooserPanel(
            'slide',
            ['core.SlidePage'],
        ),
    ]


class SlidePage(Page):
    BACKGROUND_COLOUR_CHOICES = [('WHITE', 'WHITE'), ('BLACK', 'BLACK'), ('RED', 'RED')]
    THEME_CHOICES = [('SLIDE-1', 'SLIDE-1'), ('SLIDE-2', 'SLIDE-2'), ('SLIDE-3', 'SLIDE-3'), ('SLIDE-4', 'SLIDE-4'), ('SLIDE-5', 'SLIDE-5')]
    image_background = models.ForeignKey(
        'images.CigionlineImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Background Image',
        help_text='Background image',
    )
    background_colour = CharField(blank=True, max_length=16, choices=BACKGROUND_COLOUR_CHOICES)
    body = StreamField(
        [
            ('video', blocks.StructBlock([
                ('video_url', blocks.CharBlock()),
                ('video_image', ImageChooserBlock()),
            ])),
            ('text', blocks.RichTextBlock()),
            ('separator', blocks.StructBlock()),
        ],
        blank=True,
        use_json_field=True,
    )
    timeline = StreamField(
        [
            ('slide', blocks.StructBlock(
                [
                    ('year', blocks.CharBlock()),
                    ('text', blocks.RichTextBlock()),
                    ('image', ImageChooserBlock(required=False)),
                    ('video_url', blocks.CharBlock(required=False)),
                    ('video_image', ImageChooserBlock(required=False)),
                ]
            ))
        ],
        blank=True,
        help_text='Only for timeline slide.',
        use_json_field=True,
    )
    theme = CharField(blank=False, null=True, max_length=16, choices=THEME_CHOICES)
    title_override = RichTextField(
        blank=True,
        null=False,
        features=['bold', 'italic', 'underline'],
        help_text=('The title will be replaced by this field. Leave empty to use title field.')
    )
    walls_embed = CharField(blank=True, null=True, max_length=16, help_text='Only for social slide.')

    content_panels = Page.content_panels + [
        FieldPanel('title_override'),
        FieldPanel('theme'),
        FieldPanel('image_background'),
        FieldPanel('background_colour'),
        FieldPanel('body'),
        FieldPanel('timeline'),
        FieldPanel('walls_embed'),
    ]

    parent_page_types = ['core.TwentiethPage']
    subpage_types = []
    templates = 'core/slide_page.html'

    class Meta:
        verbose_name = 'Twentieth Page Slide'


class TwentiethPageSingleton(
    ContentPage,
    BasicPageAbstract,
    FeatureablePageAbstract,
    SearchablePageAbstract,
    ShareablePageAbstract,
    ThemeablePageAbstract,
):
    body = StreamField(BasicPageAbstract.body_default_blocks + [
        ('gallery', TimelineGalleryBlock())
    ], use_json_field=True)

    content_panels = [
        BasicPageAbstract.title_panel,
        MultiFieldPanel(
            [
                FieldPanel('body'),
            ]
        ),
        MultiFieldPanel(
            [
                FieldPanel('publishing_date'),
            ],
            heading='General Information',
            classname='collapsible collapsed'
        ),
        MultiFieldPanel(
            [
                FieldPanel('topics'),
            ],
            heading='Related',
            classname='collapsible collapsed',
        )
    ]

    promote_panels = Page.promote_panels + [
        FeatureablePageAbstract.feature_panel,
        ShareablePageAbstract.social_panel,
        SearchablePageAbstract.search_panel,
    ]
    settings_panels = Page.settings_panels + [
        BasicPageAbstract.submenu_panel,
    ]

    search_fields = Page.search_fields + BasicPageAbstract.search_fields + SearchablePageAbstract.search_fields

    max_count = 1
    parent_page_types = ['core.BasicPage']
    templates = 'core/twentieth_page_singleton.html'

    class Meta:
        verbose_name = 'Twentieth Page Singleton'


class Theme(models.Model):
    name = models.CharField(max_length=255)

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_taxonomy_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name


class Think7AbstractPage(BasicPageAbstract, Page):
    """Singleton page for Think 7 abstract submission"""

    def serve(self, request):
        form = Think7AbstractUploadForm()
        email_recipient = settings.THINK7_SENDGRID_EMAIL_RECIPIENT

        if request.method == 'POST':
            form = Think7AbstractUploadForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded_file = form.cleaned_data['file']
                email = form.cleaned_data['email']
                valid_extensions = ['.pdf', '.doc', '.docx']
                file_extension = uploaded_file.name.lower().split('.')[-1]

                if f'.{file_extension}' in valid_extensions:
                    collection, created = Collection.objects.get_or_create(
                        name='Think7 Abstracts'
                    )

                    try:
                        document = Document.objects.create(
                            title=uploaded_file.name,
                            file=uploaded_file,
                            collection=collection,
                        )
                        DocumentUpload.objects.create(
                            document=document, email=email
                        )
                        if email_recipient:
                            try:
                                send_email(
                                    recipient=email_recipient,
                                    subject='New File Uploaded Successfully',
                                    body=f'File "{uploaded_file.name}" was uploaded by {email}.',
                                )
                                send_email(
                                    recipient=email,
                                    subject='Think 7 Abstract Upload Successful',
                                    body=f'Your file "{uploaded_file.name}" was uploaded successfully. Thank you for your submission to Think 7 Canada.',
                                )
                            except Exception as e:
                                print(str(e))
                        return JsonResponse(
                            {
                                'status': 'success',
                                'message': 'File uploaded successfully!',
                            }
                        )

                    except Exception as e:
                        if email_recipient:
                            send_email(
                                recipient=email_recipient,
                                subject='File Upload Failed',
                                body=f'File upload failed for {email}. Error: {str(e)}',
                            )
                        return JsonResponse(
                            {
                                'status': 'error',
                                'message': f'Failed to save file: {str(e)}',
                            }
                        )
                else:
                    if email_recipient:
                        send_email(
                            recipient=email_recipient,
                            subject='File Upload Failed',
                            body=f'File upload failed for {email}. Invalid file type.',
                        )
                return JsonResponse(
                    {
                        'status': 'error',
                        'message': 'Invalid file type. Only .pdf, .doc, and .docx files are allowed.',
                    }
                )
            else:
                error_message = " ".join(extract_errors_as_string(form.errors))

                if email_recipient:
                    send_email(
                        recipient=email_recipient,
                        subject='Form Submission Failed',
                        body=f'Form submission failed for {form.cleaned_data.get('email', 'Unknown email')}. Invalid data. {error_message}',
                    )

                return JsonResponse(
                    {'status': 'error', 'message': f'Invalid form submission. {error_message}'}
                )

        return render(request, 'think7/think7_abstract_page.html', {
            'page': self,
            'form': form,
            'self': self,
        })

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
        BasicPageAbstract.images_panel,
    ]
    settings_panels = Page.settings_panels + [
        BasicPageAbstract.submenu_panel,
    ]

    search_fields = Page.search_fields + BasicPageAbstract.search_fields

    max_count = 1
    parent_page_types = ['home.Think7HomePage']
    subpage_types = []
    template = 'think7/think7_abstract_page.html'

    class Meta:
        verbose_name = 'Think7 Abstract Page'
        verbose_name_plural = 'Think7 Abstract Pages'
