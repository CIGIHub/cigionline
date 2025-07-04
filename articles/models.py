from core.models import (
    BasicPageAbstract,
    ContentPage,
    FeatureablePageAbstract,
    FromTheArchivesPageAbstract,
    SearchablePageAbstract,
    ShareablePageAbstract,
    ThemeablePageAbstract,
)
from django.db import models
from modelcluster.fields import ParentalKey
from publications.models import PublicationPage
from streams.blocks import SeriesItemImageBlock
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.blocks import PageChooserBlock, CharBlock, StructBlock, StreamBlock
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.search import index
from wagtailmedia.edit_handlers import MediaChooserPanel
import datetime
import pytz


class ArticleLandingPage(BasicPageAbstract, SearchablePageAbstract, Page):
    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = ['articles.OpinionSeriesListPage']
    templates = 'articles/article_landing_page.html'

    def get_featured_articles(self):
        featured_article_ids = self.featured_articles.order_by('sort_order').values_list('article_page', flat=True)
        pages = Page.objects.specific().prefetch_related(
            'authors__author',
            'topics',
        ).in_bulk(featured_article_ids)
        return [pages[x] for x in featured_article_ids]

    def get_context(self, request):
        context = super().get_context(request)
        context['featured_articles'] = self.get_featured_articles()
        return context

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                InlinePanel(
                    'featured_articles',
                    max_num=15,
                    min_num=13,
                    label='Article',
                )
            ],
            heading='Featured Opinions',
            classname='collapsible collapsed',
            help_text='1: xlarge | 2: large | 3-7: small | 8-9: medium | 10-14: small | 15: large',
        )
    ]

    search_fields = Page.search_fields + BasicPageAbstract.search_fields + SearchablePageAbstract.search_fields

    class Meta:
        verbose_name = 'Article Landing Page'


class ArticleLandingPageFeaturedArticle(Orderable):
    article_landing_page = ParentalKey(
        'articles.ArticleLandingPage',
        related_name='featured_articles',
    )
    article_page = models.ForeignKey(
        'core.ContentPage',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Article',
    )

    panels = [
        PageChooserPanel(
            'article_page',
            ['articles.ArticlePage', 'articles.ArticleSeriesPage'],
        ),
    ]


class MediaLandingPage(BasicPageAbstract, SearchablePageAbstract, Page):

    def latest_cigi_in_the_news(self):
        return ArticlePage.objects.live().public().filter(article_type__title='CIGI in the News').order_by('-publishing_date')[:6]

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.hero_link_panel,
        BasicPageAbstract.body_panel,
    ]
    settings_panels = Page.settings_panels + [
        BasicPageAbstract.submenu_panel,
    ]

    search_fields = Page.search_fields + BasicPageAbstract.search_fields + SearchablePageAbstract.search_fields

    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = []
    templates = 'articles/media_landing_page.html'

    class Meta:
        verbose_name = 'Media Page'


class ArticleListPage(Page):
    max_count = 2
    parent_page_types = ['home.HomePage']
    subpage_types = ['articles.ArticlePage', 'articles.ArticleTypePage']
    templates = 'articles/article_list_page.html'

    class Meta:
        verbose_name = 'Article List Page'


class ArticlePage(
    BasicPageAbstract,
    ContentPage,
    FeatureablePageAbstract,
    FromTheArchivesPageAbstract,
    ShareablePageAbstract,
    ThemeablePageAbstract,
):
    class ArticleTypes(models.TextChoices):
        CIGI_IN_THE_NEWS = ('cigi_in_the_news', 'CIGI in the News')
        INTERVIEW = ('interview', 'Interview')
        NEWS_RELEASE = ('news_release', 'News Release')
        OP_ED = ('op_ed', 'Op-Ed')
        OPINION = ('opinion', 'Opinion')

    class Languages(models.TextChoices):
        DA = ('da', 'Danish')
        DE = ('de', 'German')
        EL = ('el', 'Greek')
        EN = ('en', 'English')
        ES = ('es', 'Spanish')
        FR = ('fr', 'French')
        ID = ('id', 'Indonesian')
        IT = ('it', 'Italian')
        NL = ('nl', 'Dutch')
        PL = ('pl', 'Polish')
        PT = ('pt', 'Portugese')
        RO = ('ro', 'Romanian')
        SK = ('sk', 'Slovak')
        SV = ('sv', 'Swedish')
        TR = ('tr', 'Turkish')
        ZH = ('zh', 'Chinese')

    class HeroTitlePlacements(models.TextChoices):
        BOTTOM = ('bottom', 'Bottom')
        TOP = ('top', 'Top')

    article_series = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Essay series',
    )
    article_type = models.ForeignKey(
        'articles.ArticleTypePage',
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name='articles',
    )
    body = StreamField(
        BasicPageAbstract.body_default_blocks + [
            BasicPageAbstract.body_accordion_block,
            BasicPageAbstract.body_autoplay_video_block,
            BasicPageAbstract.body_chart_block,
            BasicPageAbstract.body_embedded_tiktok_block,
            BasicPageAbstract.body_external_quote_block,
            BasicPageAbstract.body_external_video_block,
            BasicPageAbstract.body_extract_block,
            BasicPageAbstract.body_highlight_title_block,
            BasicPageAbstract.body_image_full_bleed_block,
            BasicPageAbstract.body_image_scroll_block,
            BasicPageAbstract.body_poster_block,
            BasicPageAbstract.body_pull_quote_left_block,
            BasicPageAbstract.body_pull_quote_right_block,
            BasicPageAbstract.body_recommended_block,
            BasicPageAbstract.body_text_border_block,
            BasicPageAbstract.body_tool_tip_block,
            BasicPageAbstract.body_tweet_block,
            BasicPageAbstract.additional_image_block,
            BasicPageAbstract.additional_disclaimer_block,
            BasicPageAbstract.line_break_block,
        ],
        blank=True,
        use_json_field=True,
    )
    canonical_link = models.URLField(
        blank=True,
        max_length=512,
        help_text='An external URL (https://...) or an internal URL (/interactives/2019annualreport/).',
    )
    embed_youtube = models.URLField(
        blank=True,
        verbose_name='YouTube Embed',
        help_text='Enter the YouTube URL (https://www.youtube.com/watch?v=4-Xkn1U1DkA) or short URL (https://youtu.be/o5acQ2GxKbQ) to add an embedded video.',
    )
    embed_youtube_label = models.CharField(
        max_length=255,
        blank=True,
        help_text='Add a label to appear below the embedded video.',
    )
    footnotes = RichTextField(
        blank=True,
        features=[
            'bold',
            'endofarticle',
            'h3',
            'h4',
            'italic',
            'link',
            'ol',
            'ul',
            'subscript',
            'superscript',
            'anchor',
        ],
    )
    hero_title_placement = models.CharField(
        blank=True,
        max_length=16,
        choices=HeroTitlePlacements.choices,
        verbose_name='Hero Title Placement',
        help_text='Placement of the title within the hero section. Currently only works on the Longform 2 theme.',
    )
    hide_excerpt = models.BooleanField(
        default=False,
        verbose_name='Hide Excerpt',
        help_text='For "CIGI in the News" only: when enabled, hide excerpt and display full article instead',
    )
    image_banner = models.ForeignKey(
        'images.CigionlineImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Banner Image',
    )
    image_banner_small = models.ForeignKey(
        'images.CigionlineImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Banner Image Small'
    )
    image_poster = models.ForeignKey(
        'images.CigionlineImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Poster Image',
        help_text='A poster image used in feature sections',
    )
    interviewers = StreamField(
        [
            ('interviewer', PageChooserBlock(required=True, page_type='people.PersonPage')),
        ],
        blank=True,
        use_json_field=True,
    )
    language = models.CharField(
        blank=True,
        max_length=2,
        choices=Languages.choices,
        verbose_name='Language',
        help_text='If this content is in a language other than English, please select the language from the list.',
    )
    multimedia_series = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    opinion_series = models.ForeignKey(
        'articles.OpinionSeriesPage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    related_files = StreamField(
        [
            ('file', DocumentChooserBlock()),
        ],
        blank=True,
        use_json_field=True,
    )
    short_description = RichTextField(
        blank=True,
        null=False,
        features=['bold', 'italic', 'link'],
    )
    video_banner = models.ForeignKey(
        'wagtailmedia.Media',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Banner Video',
    )
    website_button_text = models.CharField(
        blank=True,
        max_length=64,
        help_text='Override the button text for the article website. If empty, the button will read "View Full Article".'
    )
    website_url = models.URLField(blank=True, max_length=512)
    works_cited = RichTextField(
        blank=True,
        features=[
            'bold',
            'endofarticle',
            'h3',
            'h4',
            'italic',
            'link',
            'ol',
            'ul',
            'subscript',
            'superscript',
        ],
    )

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_node_id = models.IntegerField(blank=True, null=True)

    @property
    def cigi_people_mentioned_ids(self):
        return [item.person.id for item in self.cigi_people_mentioned.all()]

    @property
    def expired_image(self):
        if self.publishing_date:
            return self.publishing_date < datetime.datetime(2017, 1, 1).astimezone(pytz.timezone('America/Toronto'))
        return False

    @property
    def article_series_description(self):
        if self.article_series:
            return self.article_series.specific.series_items_description
        return None

    @property
    def article_series_disclaimer(self):
        if self.article_series:
            for series_item in self.article_series.specific.article_series_items:
                if series_item.content_page.specific == self and not series_item.hide_series_disclaimer:
                    return self.article_series.specific.series_items_disclaimer
        return None

    @property
    def opinion_series_pages(self):
        if self.opinion_series:
            return ArticlePage.objects.live().public().filter(opinion_series=self.opinion_series).exclude(id=self.id)
        return None

    @property
    def opinion_series_description(self):
        if self.opinion_series:
            return self.opinion_series.specific.series_items_description
        return None

    def is_opinion(self):
        return self.article_type.title in [
            'Op-Eds',
            'Opinion',
        ]

    def get_template(self, request, *args, **kwargs):
        standard_template = super(ArticlePage, self).get_template(request, *args, **kwargs)
        if self.theme:
            return f'themes/{self.get_theme_dir()}/article_page.html'
        return standard_template

    def get_additional_images(self):
        additional_images = []

        for block in self.body:
            if block.block_type == 'additional_image':
                additional_images.append(block.value)
        return additional_images

    def get_additional_disclaimers(self):
        additional_disclaimers = []

        for block in self.body:
            if block.block_type == 'additional_disclaimer':
                additional_disclaimers.append(block.value)
        return additional_disclaimers

    def get_series_article_category(self):
        article_series_page = self.article_series.specific
        current_series_title = article_series_page.series_items.first().category_title
        for series_item in article_series_page.series_items.all():
            if series_item.category_title:
                current_series_title = series_item.category_title
            if series_item.content_page.id == self.id:
                return current_series_title

    content_panels = [
        BasicPageAbstract.title_panel,
        MultiFieldPanel(
            [
                FieldPanel('short_description'),
                FieldPanel('body'),
                FieldPanel('footnotes'),
                FieldPanel('works_cited'),
            ],
            heading='Body',
            classname='collapsible collapsed'
        ),
        MultiFieldPanel(
            [
                PageChooserPanel(
                    'article_type',
                    ['articles.ArticleTypePage'],
                ),
                FieldPanel('hide_excerpt'),
                FieldPanel('publishing_date'),
                FieldPanel('website_url'),
                FieldPanel('website_button_text'),
                FieldPanel('language'),
            ],
            heading='General Information',
            classname='collapsible collapsed',
        ),
        ContentPage.authors_panel,
        MultiFieldPanel(
            [
                FieldPanel('image_hero'),
                FieldPanel('image_poster'),
                FieldPanel('image_banner'),
                FieldPanel('image_banner_small'),
            ],
            heading='Images',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('embed_youtube'),
                FieldPanel('embed_youtube_label'),
                MediaChooserPanel('video_banner'),
            ],
            heading='Media',
            classname='collapsible collapsed',
        ),
        ContentPage.recommended_panel,
        MultiFieldPanel(
            [
                FieldPanel('topics'),
                FieldPanel('projects'),
                FieldPanel('countries'),
                PageChooserPanel(
                    'article_series',
                    ['articles.ArticleSeriesPage'],
                ),
                PageChooserPanel(
                    'multimedia_series',
                    ['multimedia.MultimediaSeriesPage'],
                ),
                PageChooserPanel(
                    'opinion_series',
                    ['articles.OpinionSeriesPage'],
                ),
                InlinePanel('cigi_people_mentioned', label='People Mentioned'),
                FieldPanel('interviewers'),
                FieldPanel('related_files'),
            ],
            heading='Related',
            classname='collapsible collapsed',
        ),
        FromTheArchivesPageAbstract.from_the_archives_panel,
    ]
    promote_panels = Page.promote_panels + [
        FeatureablePageAbstract.feature_panel,
        ShareablePageAbstract.social_panel,
        SearchablePageAbstract.search_panel,
    ]
    settings_panels = Page.settings_panels + [
        ThemeablePageAbstract.theme_panel,
        FieldPanel('canonical_link'),
    ]

    search_fields = BasicPageAbstract.search_fields \
        + ContentPage.search_fields \
        + [
            index.FilterField('article_type'),
            index.FilterField('cigi_people_mentioned_ids'),
            index.FilterField('publishing_date'),
            index.FilterField('opinion_series'),
        ]

    parent_page_types = ['articles.ArticleListPage']
    subpage_types = []
    templates = 'articles/article_page.html'

    @property
    def is_title_bottom(self):
        return self.title in ['Can the G20 Save Globalization\'s Waning Reputation?', 'Shoshana Zuboff on the Undetectable, Indecipherable World of Surveillance Capitalism']

    @property
    def article_series_category(self):
        if self.article_series:
            category = ''
            for series_item in self.article_series.specific.article_series_items:
                if series_item.category_title:
                    category = series_item.category_title
                if series_item.content_page.id == self.id:
                    return category
        return ''

    class Meta:
        verbose_name = 'Opinion'
        verbose_name_plural = 'Opinions'


class ArticlePagePersonMentioned(Orderable):
    article_page = ParentalKey(
        'articles.ArticlePage',
        related_name='cigi_people_mentioned',
    )
    person = models.ForeignKey(
        'people.PersonPage',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Person',
    )

    panels = [
        PageChooserPanel(
            'person',
            ['people.PersonPage'],
        ),
    ]


class ArticleTypePage(BasicPageAbstract, Page):
    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_taxonomy_id = models.IntegerField(blank=True, null=True)

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
    ]
    settings_panels = Page.settings_panels + [
        BasicPageAbstract.submenu_panel,
    ]

    search_fields = Page.search_fields + BasicPageAbstract.search_fields

    parent_page_types = ['articles.ArticleListPage', 'publications.PublicationListPage']
    subpage_types = []
    templates = 'articles/article_type_page.html'

    class Meta:
        verbose_name = 'Article Type'
        verbose_name_plural = 'Article Types'


class ArticleSeriesListPage(BasicPageAbstract, Page):
    max_count = 1
    parent_page_types = ['home.HomePage', 'publications.PublicationListPage']
    subpage_types = ['articles.ArticleSeriesPage']
    templates = 'articles/article_series_list_page.html'

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
        verbose_name = 'Article Series List Page'


class ArticleSeriesPage(
    BasicPageAbstract,
    ContentPage,
    FeatureablePageAbstract,
    FromTheArchivesPageAbstract,
    ShareablePageAbstract,
    ThemeablePageAbstract,
):
    acknowledgements = RichTextField(
        blank=True,
        features=[
            'bold',
            'italic',
            'link',
            'h2',
            'h3',
            'h4',
        ],
    )
    credits = RichTextField(
        blank=True,
        features=[
            'bold',
            'italic',
            'link',
            'name',
        ],
    )
    credits_stream_field = StreamField(
        [
            ('title', StructBlock([
                ('title', CharBlock()),
                ('people', StreamBlock([
                    ('name', CharBlock())
                ])),
            ]))
        ],
        blank=True,
        use_json_field=True,
    )
    credits_artwork = models.CharField(
        max_length=255,
        blank=True,
    )
    featured_items = StreamField(
        [
            ('featured_item', PageChooserBlock(
                required=True,
                page_type=['articles.ArticlePage', 'multimedia.MultimediaPage'],
            )),
        ],
        blank=True,
        use_json_field=True,
    )
    image_banner = models.ForeignKey(
        'images.CigionlineImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Banner Image',
    )
    image_banner_small = models.ForeignKey(
        'images.CigionlineImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Banner Image Small'
    )
    image_poster = models.ForeignKey(
        'images.CigionlineImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Poster image',
        help_text='A poster image which will be used in the highlights section of the homepage.',
    )
    short_description = RichTextField(
        blank=True,
        null=False,
        features=['bold', 'italic', 'link'],
    )
    series_items_description = RichTextField(
        blank=True,
        null=True,
        features=['bold', 'italic', 'link'],
    )
    series_videos_description = RichTextField(
        blank=True,
        null=True,
        features=['bold', 'italic', 'link'],
        help_text='To be displayed on video/multimedia pages of the series in place of Series Items Description'
    )
    series_items_disclaimer = RichTextField(
        blank=True,
        null=True,
        features=['bold', 'italic', 'link'],
    )
    video_banner = models.ForeignKey(
        'wagtailmedia.Media',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Banner Video',
    )

    @property
    def image_poster_caption(self):
        return self.image_poster.caption

    @property
    def image_poster_url(self):
        return self.image_poster.get_rendition('fill-672x895').url

    @property
    def article_series_items(self):
        return self.series_items.prefetch_related(
            'content_page',
            'content_page__authors__author',
        ).all()

    @property
    def series_pdf(self):
        publication_page = PublicationPage.objects.filter(title=self.title).first()
        try:
            pdf_downloads = [
                {
                    'type': pdf.value['button_text'] if pdf.value['button_text'] else 'Download PDF',
                    'url': pdf.value['file'].url
                }
                for pdf in publication_page.pdf_downloads
            ]
            return pdf_downloads
        except AttributeError:
            return []

    def series_items_by_category(self):
        series_items = self.article_series_items
        series_items_by_category = []
        for series_item in series_items:
            category = series_item.category_title
            if category:
                series_items_by_category.append({
                    'category': category,
                    'series_items': [series_item.content_page],
                    'live': series_item.content_page.live,
                })
            else:
                series_items_by_category[-1]['series_items'].append(series_item.content_page)
        return series_items_by_category

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_node_id = models.IntegerField(blank=True, null=True)

    def get_template(self, request, *args, **kwargs):
        standard_template = super(ArticleSeriesPage, self).get_template(request, *args, **kwargs)
        if self.theme:
            return f'themes/{self.get_theme_dir()}/article_series_page.html'
        return standard_template

    content_panels = [
        BasicPageAbstract.title_panel,
        MultiFieldPanel(
            [
                FieldPanel('short_description'),
                FieldPanel('body'),
            ],
            heading='Body',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('publishing_date'),
            ],
            heading='General Information',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('series_items_description'),
                FieldPanel('series_videos_description'),
                FieldPanel('series_items_disclaimer'),
                InlinePanel('series_items'),
            ],
            heading='Series Items',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('acknowledgements'),
                FieldPanel('credits_artwork'),
                FieldPanel('credits_stream_field'),
            ],
            heading='Credits',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('image_hero'),
                FieldPanel('image_banner'),
                FieldPanel('image_banner_small'),
                FieldPanel('image_poster'),
            ],
            heading='Image',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                MediaChooserPanel('video_banner'),
            ],
            heading='Media',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('featured_items'),
            ],
            heading='Featured Series Items',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('topics'),
                FieldPanel('projects'),
                FieldPanel('countries'),
            ],
            heading='Related',
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

    search_fields = Page.search_fields \
        + BasicPageAbstract.search_fields \
        + ContentPage.search_fields

    parent_page_types = ['home.HomePage', 'home.Think7HomePage']
    subpage_types = []
    templates = 'articles/article_series_page.html'

    @property
    def series_contributors_by_article(self):
        series_contributors = []
        item_people = set()

        for series_item in self.article_series_items:
            people = series_item.content_page.authors.all()
            people_string = ''

            for person in people:
                person_string = person.author.title
                people_string += person_string

                # Add each person as well so if there's an article with just
                # a single author who's already been in another article in
                # collaboration, then we won't add their name to the list
                # again.
                if len(people) > 1:
                    item_people.add(person_string)

            if people_string not in item_people:
                series_contributors.append({'item': series_item.content_page, 'contributors': people})
                item_people.add(people_string)

        return series_contributors

    @property
    def series_contributors(self):
        series_contributors = []
        item_people = set()

        for series_item in self.article_series_items:
            people = series_item.content_page.authors.all()
            for person in people:
                if person.author.title not in item_people:
                    series_contributors.append({
                        'id': person.author.id,
                        'title': person.author.title,
                        'url': person.author.url,
                    })
                    item_people.add(person.author.title)
        return series_contributors

    @property
    def series_contributors_by_person(self):
        # Series contributors ordered by last name
        series_contributors = []
        item_people = set()

        for series_item in self.article_series_items:
            people = series_item.content_page.authors.all()

            # Skip items that have more than 2 authors/speakers. For
            # example, in the After COVID series, there is an introductory
            # video with many authors.
            if len(people) > 2:
                continue
            else:
                for person in people:
                    if person.author.title not in item_people:
                        series_contributors.append({
                            'item': series_item.content_page,
                            'contributors': [person.author],
                            'last_name': person.author.last_name,
                        })
                        item_people.add(person.author.title)

        series_contributors.sort(key=lambda x: x['last_name'])
        return series_contributors

    @property
    def series_authors(self):
        series_authors = []
        series_people = set()
        for series_item in self.article_series_items:
            people = series_item.content_page.authors.all()
            for person in people:
                if person.author.title not in series_people:
                    series_authors.append(person.author)
                    series_people.add(person.author.title)
        return series_authors

    @property
    def series_authors_by_article(self):
        '''
        Similar to 'series_contribitors_by_article', but only for authors of article pages
        '''
        series_authors = []
        item_people = set()

        for series_item in self.article_series_items:
            if series_item.content_page.contenttype == 'Opinion':
                people = series_item.content_page.authors.all()
                people_string = ''

                for person in people:
                    person_string = person.author.title
                    people_string += person_string

                    if len(people) > 1:
                        item_people.add(person_string)

                if people_string not in item_people:
                    series_authors.append({'item': series_item.content_page, 'authors': people})
                    item_people.add(people_string)

        return series_authors

    class Meta:
        verbose_name = 'Essay Series'
        verbose_name_plural = 'Essay Series'


class ArticleSeriesPageSeriesItem(Orderable):
    article_series_page = ParentalKey(
        'articles.ArticleSeriesPage',
        related_name='series_items',
    )
    content_page = models.ForeignKey(
        'core.ContentPage',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Series Item',
    )
    category_title = models.CharField(blank=True, max_length=255)
    hide_series_disclaimer = models.BooleanField(default=False)
    additional_fields = StreamField(
        [
            ('image', SeriesItemImageBlock()),
        ],
        blank=True,
        use_json_field=True,
    )

    def image_override(self):
        image = [field for field in self.additional_fields if field.block_type == 'image']
        if not image:
            return None

        image = image[0].value.get('image')
        image_override = {}
        if image.file.url.endswith('.gif'):
            image_override['src_gif'] = image.file.url
            image_override['src_static'] = image.get_rendition('original').file.url
        else:
            image_override['src_static'] = image.get_rendition('fill-300x300').file.url
        image_override['alt'] = image.caption if image.caption else image.title
        return image_override

    panels = [
        FieldPanel('category_title'),
        PageChooserPanel(
            'content_page',
            ['articles.ArticlePage', 'multimedia.MultimediaPage', 'events.EventPage'],
        ),
        FieldPanel('hide_series_disclaimer'),
        FieldPanel('additional_fields'),
    ]


class OpinionSeriesPage(
    BasicPageAbstract,
    ContentPage,
    FeatureablePageAbstract,
    FromTheArchivesPageAbstract,
    ShareablePageAbstract,
    ThemeablePageAbstract,
):

    image_banner = models.ForeignKey(
        'images.CigionlineImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Banner Image',
    )
    series_items_description = RichTextField(
        blank=True,
        null=True,
        features=['bold', 'italic', 'link'],
    )

    series_items_disclaimer = RichTextField(
        blank=True,
        null=True,
        features=['bold', 'italic', 'link'],
    )

    @property
    def series_authors(self):
        authors = set()
        opinions = ArticlePage.objects.live().public().filter(opinion_series=self)
        for opinion in opinions:
            for author in opinion.authors.all():
                authors.add(author.author)
        authors_list = list(authors)
        authors_list.sort(key=lambda x: x.last_name)
        return authors_list

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
        MultiFieldPanel(
            [
                FieldPanel('publishing_date'),
            ],
            heading='General Information',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('image_hero'),
                FieldPanel('image_banner'),
            ],
            heading='Images',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('series_items_description'),
                FieldPanel('series_items_disclaimer'),
            ],
            heading='Series Items',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('topics'),
                FieldPanel('projects'),
                FieldPanel('countries'),
            ],
            heading='Related',
            classname='collapsible collapsed',
        ),
    ]
    promote_panels = Page.promote_panels + [
        FeatureablePageAbstract.feature_panel,
        SearchablePageAbstract.search_panel,
    ]

    search_fields = ContentPage.search_fields + BasicPageAbstract.search_fields + [
        index.FilterField('series_authors'),
        index.FilterField('publishing_date'),
    ]

    parent_page_types = ['articles.OpinionSeriesListPage']
    subpage_types = []
    templates = 'articles/opinion_series_page.html'

    class Meta:
        verbose_name = 'Opinion Series'
        verbose_name_plural = 'Opinion Series'


class OpinionSeriesListPage(
        BasicPageAbstract,
        ContentPage,
        FeatureablePageAbstract,
        FromTheArchivesPageAbstract,
        ShareablePageAbstract,
        ThemeablePageAbstract
):

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
        MultiFieldPanel(
            [
                FieldPanel('publishing_date'),
            ],
            heading='General Information',
            classname='collapsible collapsed',
        ),
        BasicPageAbstract.images_panel,
    ]

    promote_panels = Page.promote_panels + [
        FeatureablePageAbstract.feature_panel,
        SearchablePageAbstract.search_panel,
    ]

    search_fields = ContentPage.search_fields + BasicPageAbstract.search_fields

    max_count = 1
    parent_page_types = ['home.HomePage', 'articles.ArticleListPage', 'articles.ArticleLandingPage']
    subpage_types = ['articles.OpinionSeriesPage']
    templates = 'articles/opinion_series_list_page.html'

    class Meta:
        verbose_name = 'Opinion Series List Page'
