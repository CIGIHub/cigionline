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
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
    StreamFieldPanel,
)
from wagtail.core.blocks import PageChooserBlock
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable, Page
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtailmedia.edit_handlers import MediaChooserPanel
import datetime
import pytz


class ArticleLandingPage(BasicPageAbstract, Page):
    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = []
    templates = 'articles/article_landing_page.html'

    def get_featured_articles(self):
        featured_article_ids = self.featured_articles.order_by('sort_order').values_list('article_page', flat=True)
        pages = Page.objects.specific().prefetch_related(
            'authors__author',
            'topics',
        ).in_bulk(featured_article_ids)
        return [pages[x] for x in featured_article_ids]

    def get_featured_article_series(self):
        return ArticleSeriesPage.objects.prefetch_related(
            'topics',
        ).live().public().order_by('-publishing_date')[:10]

    def get_context(self, request):
        context = super().get_context(request)
        context['featured_articles'] = self.get_featured_articles()
        context['featured_article_series'] = self.get_featured_article_series()
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

    search_fields = Page.search_fields + BasicPageAbstract.search_fields

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


class MediaLandingPage(BasicPageAbstract, Page):

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

    search_fields = Page.search_fields + BasicPageAbstract.search_fields

    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = []
    templates = 'articles/media_landing_page.html'

    class Meta:
        verbose_name = 'Media Page'


class ArticleListPage(Page):
    max_count = 1
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
        verbose_name='Opinion series',
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
        ],
        blank=True,
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
    related_files = StreamField(
        [
            ('file', DocumentChooserBlock()),
        ],
        blank=True,
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

    content_panels = [
        BasicPageAbstract.title_panel,
        MultiFieldPanel(
            [
                FieldPanel('short_description'),
                StreamFieldPanel('body'),
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
                ImageChooserPanel('image_hero'),
                ImageChooserPanel('image_poster'),
                ImageChooserPanel('image_banner'),
                ImageChooserPanel('image_banner_small'),
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
                PageChooserPanel(
                    'article_series',
                    ['articles.ArticleSeriesPage'],
                ),
                PageChooserPanel(
                    'multimedia_series',
                    ['multimedia.MultimediaSeriesPage'],
                ),
                InlinePanel('cigi_people_mentioned', label='People Mentioned'),
                StreamFieldPanel('interviewers'),
                StreamFieldPanel('related_files'),
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
    ]

    search_fields = BasicPageAbstract.search_fields \
        + ContentPage.search_fields \
        + [
            index.FilterField('article_type'),
            index.FilterField('cigi_people_mentioned_ids'),
            index.FilterField('publishing_date'),
        ]

    parent_page_types = ['articles.ArticleListPage']
    subpage_types = []
    templates = 'articles/article_page.html'

    @property
    def is_title_bottom(self):
        return self.title in ['Can the G20 Save Globalization\'s Waning Reputation?', 'Shoshana Zuboff on the Undetectable, Indecipherable World of Surveillance Capitalism']

    @property
    def article_series_category(self):
        category = ''
        for series_item in self.article_series.specific.article_series_items:
            if series_item.category_title:
                category = series_item.category_title
            if series_item.content_page.id == self.id:
                return category

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

    parent_page_types = ['articles.ArticleListPage']
    subpage_types = []
    templates = 'articles/article_type_page.html'

    class Meta:
        verbose_name = 'Article Type'
        verbose_name_plural = 'Article Types'


class ArticleSeriesListPage(Page):
    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = []
    templates = 'articles/article_series_list_page.html'

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
    credits = RichTextField(
        blank=True,
        features=[
            'bold',
            'italic',
            'link',
            'name',
        ],
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
                StreamFieldPanel('body'),
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
                FieldPanel('series_items_disclaimer'),
                InlinePanel('series_items'),
            ],
            heading='Series Items',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('credits'),
                FieldPanel('credits_artwork'),
            ],
            heading='Credits',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                ImageChooserPanel('image_hero'),
                ImageChooserPanel('image_banner'),
                ImageChooserPanel('image_banner_small'),
                ImageChooserPanel('image_poster'),
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
                StreamFieldPanel('featured_items'),
            ],
            heading='Featured Series Items',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('topics'),
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

    parent_page_types = ['home.HomePage']
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

    class Meta:
        verbose_name = 'Opinion Series'
        verbose_name_plural = 'Opinion Series'


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

    panels = [
        FieldPanel('category_title'),
        PageChooserPanel(
            'content_page',
            ['articles.ArticlePage', 'multimedia.MultimediaPage', 'events.EventPage'],
        ),
        FieldPanel('hide_series_disclaimer'),
    ]
