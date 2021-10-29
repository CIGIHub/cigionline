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
from streams.blocks import PodcastSubscribeButtonBlock
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
    StreamFieldPanel,
)
from wagtail.core.blocks import (
    CharBlock,
    IntegerBlock,
    StructBlock,
    TextBlock,
)
from wagtail.core.fields import StreamField
from wagtail.core.models import Orderable, Page
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index


class MultimediaListPage(BasicPageAbstract, Page):
    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = ['multimedia.MultimediaPage']
    template = 'multimedia/multimedia_list_page.html'
    ajax_template = 'includes/multimedia_list_page_multimedia_list.html'

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
        BasicPageAbstract.images_panel,
        MultiFieldPanel(
            [
                InlinePanel(
                    'featured_multimedia',
                    max_num=6,
                    min_num=0,
                    label='Multimedia',
                ),
            ],
            heading='Featured Multimedia',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                InlinePanel(
                    'promotion_blocks',
                    max_num=2,
                    min_num=0,
                    label='Promotion Block',
                ),
            ],
            heading='Promotion Blocks',
            classname='collapsible collapsed',
        ),
    ]
    settings_panels = Page.settings_panels + [
        BasicPageAbstract.submenu_panel,
    ]

    search_fields = Page.search_fields + BasicPageAbstract.search_fields

    def get_featured_multimedia(self):
        featured_multimedia_ids = self.featured_multimedia.order_by('sort_order').values_list('multimedia_page', flat=True)
        pages = Page.objects.specific().prefetch_related(
            'authors__author',
            'topics',
        ).in_bulk(featured_multimedia_ids)
        return [pages[x] for x in featured_multimedia_ids]

    def get_promotion_blocks(self):
        return self.promotion_blocks.prefetch_related(
            'promotion_block',
        ).all()[:1]

    def get_context(self, request):
        context = super().get_context(request)
        context['featured_multimedia'] = self.get_featured_multimedia()
        context['promotion_blocks'] = self.get_promotion_blocks()
        return context

    class Meta:
        verbose_name = 'Multimedia List Page'


class MultimediaListPageFeaturedMultimedia(Orderable):
    multimedia_list_page = ParentalKey(
        'multimedia.MultimediaListPage',
        related_name='featured_multimedia',
    )
    multimedia_page = models.ForeignKey(
        'wagtailcore.Page',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Multimedia',
    )

    panels = [
        PageChooserPanel(
            'multimedia_page',
            ['multimedia.MultimediaPage'],
        )
    ]


class MultimediaPage(
    BasicPageAbstract,
    ContentPage,
    FeatureablePageAbstract,
    FromTheArchivesPageAbstract,
    ShareablePageAbstract,
    ThemeablePageAbstract,
):
    class MultimediaTypes(models.TextChoices):
        AUDIO = ('audio', 'Audio')
        VIDEO = ('video', 'Video')

    article_series = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Opinion series',
    )
    companion_essay = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Companion essay',
    )
    image_banner = models.ForeignKey(
        'images.CigionlineImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Banner Image',
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
    image_square = models.ForeignKey(
        'images.CigionlineImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Square image',
    )
    multimedia_series = models.ForeignKey(
        'multimedia.MultimediaSeriesPage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    multimedia_type = models.CharField(
        blank=False,
        max_length=8,
        choices=MultimediaTypes.choices,
        default=MultimediaTypes.VIDEO,
    )
    multimedia_url = models.URLField(
        blank=True,
        verbose_name='Multimedia URL',
        help_text='The URL of the multimedia source from YouTube or Simplecast.',
    )
    podcast_audio_duration = models.CharField(blank=True, max_length=8)
    podcast_audio_file_size = models.IntegerField(blank=True, null=True)
    podcast_audio_url = models.URLField(blank=True)
    podcast_episode = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Episode Number',
    )
    podcast_guests = StreamField(
        [
            ('guest', CharBlock(required=True)),
        ],
        blank=True,
    )
    podcast_season = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Season Number',
    )
    podcast_subtitle = models.CharField(blank=True, max_length=255)
    podcast_video_duration = models.CharField(blank=True, max_length=8)
    podcast_video_file_size = models.IntegerField(blank=True, null=True)
    podcast_video_url = models.URLField(blank=True)
    transcript = StreamField(
        [
            BasicPageAbstract.body_accordion_block,
            BasicPageAbstract.body_read_more_block,
        ],
        blank=True,
    )
    video_chapters = StreamField(
        [
            ('video_chapter', StructBlock([
                ('chapter_title', CharBlock(required=True)),
                ('location_time', IntegerBlock(required=True)),
                ('chapter_description', TextBlock(required=False)),
            ])),
        ],
        blank=True,
    )
    youtube_id = models.CharField(
        blank=True,
        max_length=32,
        verbose_name='YouTube ID',
        help_text='Enter just the YouTube ID for this video. This is the series of letters and numbers found either at www.youtube.com/embed/[here], or www.youtube.com/watch?v=[here]. This is used for the video chaptering below.',
    )

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_node_id = models.IntegerField(blank=True, null=True)

    def get_template(self, request, *args, **kwargs):
        standard_template = super(MultimediaPage, self).get_template(request, *args, **kwargs)
        if self.theme:
            return f'themes/{self.get_theme_dir()}/multimedia_page.html'
        return standard_template

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
        MultiFieldPanel(
            [
                FieldPanel('multimedia_type'),
                FieldPanel('publishing_date'),
                FieldPanel('multimedia_url'),
            ],
            heading='General Information',
            classname='collapsible',
        ),
        MultiFieldPanel(
            [
                InlinePanel('authors'),
            ],
            heading='Speakers',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('youtube_id'),
                StreamFieldPanel('video_chapters'),
            ],
            heading='Video Chapters',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                StreamFieldPanel('transcript'),
            ],
            heading='Transcript',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('podcast_subtitle'),
                FieldPanel('podcast_season'),
                FieldPanel('podcast_episode'),
                StreamFieldPanel('podcast_guests'),
                MultiFieldPanel(
                    [
                        FieldPanel('podcast_audio_url'),
                        FieldPanel('podcast_audio_duration'),
                        FieldPanel('podcast_audio_file_size'),
                    ],
                    heading='Audio',
                    classname='collapsible collapsed',
                ),
                MultiFieldPanel(
                    [
                        FieldPanel('podcast_video_url'),
                        FieldPanel('podcast_video_duration'),
                        FieldPanel('podcast_video_file_size'),
                    ],
                    heading='Video',
                    classname='collapsible collapsed',
                ),
            ],
            heading='Podcast Details',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                ImageChooserPanel('image_hero'),
                ImageChooserPanel('image_banner'),
                ImageChooserPanel('image_square'),
                ImageChooserPanel('image_poster'),
            ],
            heading='Images',
            classname='collapsible collapsed',
        ),
        ContentPage.recommended_panel,
        MultiFieldPanel(
            [
                PageChooserPanel(
                    'multimedia_series',
                    ['multimedia.MultimediaSeriesPage'],
                ),
                PageChooserPanel(
                    'article_series',
                    ['articles.ArticleSeriesPage'],
                ),
                PageChooserPanel(
                    'companion_essay',
                    ['articles.ArticlePage'],
                ),
                FieldPanel('topics'),
                FieldPanel('projects'),
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
            index.FilterField('multimedia_series'),
            index.FilterField('multimedia_type'),
            index.FilterField('publishing_date'),
        ]

    parent_page_types = ['multimedia.MultimediaListPage', 'multimedia.MultimediaSeriesPage']
    subpage_types = []
    templates = 'multimedia/multimedia_page.html'

    class Meta:
        verbose_name = 'Multimedia'
        verbose_name_plural = 'Multimedia'


class MultimediaSeriesListPage(Page):
    """
    A singleton page that isn't published, but is the parent to all the
    multimedia series pages at the path /multimedia-series.
    """
    max_count = 1
    parent_page_types = ['home.HomePage']
    subpage_types = ['multimedia.MultimediaSeriesPage']
    templates = 'multimedia/multimedia_series_list_page.html'

    class Meta:
        verbose_name = 'Multimedia Series List Page'


class MultimediaSeriesPage(
    BasicPageAbstract,
    ContentPage,
    FeatureablePageAbstract,
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
    image_logo = models.ForeignKey(
        'images.CigionlineImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Series Logo',
    )
    image_poster = models.ForeignKey(
        'images.CigionlineImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Poster Image',
        help_text='A poster image which will be used in the highlights section of the homepage.',
    )
    podcast_apple_url = models.URLField(
        blank=True,
        verbose_name='Apple Podcast URL',
        help_text='Enter the link to the Apple Podcast landing page for this podcast.',
    )
    podcast_google_url = models.URLField(
        blank=True,
        verbose_name='Google Podcast URL',
        help_text='Enter the link to the Google Podcast landing page for the podcast.',
    )
    podcast_spotify_url = models.URLField(
        blank=True,
        verbose_name='Spotify Podcast URL',
        help_text='Enter the link to the Spotify Podcast landing page for the podcast.',
    )

    podcast_subscribe_buttons = StreamField([
            ('podcast_subscribe_button', PodcastSubscribeButtonBlock())
        ],
        blank=True,
        help_text='A list of search terms for which this page will be elevated in the search results.',
    )

    @property
    def series_seasons(self):
        episode_filter = {
            'multimedia_series': self,
            'theme__name__in': [
                'Big Tech S3',
                'Big Tech',
            ]
        }
        series_episodes = MultimediaPage.objects.filter(**episode_filter).order_by('-publishing_date')
        series_seasons = {}
        for episode in series_episodes:
            episode_season = episode.specific.podcast_season
            if episode_season not in series_seasons:
                series_seasons.update({episode_season: {'published': [], 'unpublished': []}})
            if episode.live:
                series_seasons[episode_season]['published'].append(episode)
            else:
                series_seasons[episode_season]['unpublished'].append(episode)

        return series_seasons

    @property
    def latest_episode(self):
        return MultimediaPage.objects.filter(multimedia_series=self).live().latest('publishing_date')

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_node_id = models.IntegerField(blank=True, null=True)

    content_panels = [
        BasicPageAbstract.title_panel,
        BasicPageAbstract.body_panel,
        MultiFieldPanel(
            [
                FieldPanel('publishing_date'),
            ],
            heading='General Information',
            classname='collapsible',
        ),
        MultiFieldPanel(
            [
                ImageChooserPanel('image_hero'),
                ImageChooserPanel('image_banner'),
                ImageChooserPanel('image_poster'),
            ],
            heading='Images',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                ImageChooserPanel('image_logo'),
                FieldPanel('podcast_apple_url'),
                FieldPanel('podcast_spotify_url'),
                FieldPanel('podcast_google_url'),
                StreamFieldPanel('podcast_subscribe_buttons'),
            ],
            heading='Podcast Details',
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
    search_fields = ContentPage.search_fields + BasicPageAbstract.search_fields

    parent_page_types = ['home.HomePage', 'multimedia.MultimediaSeriesListPage']
    subpage_types = ['multimedia.MultimediaPage']
    templates = 'multimedia/multimedia_series_page.html'

    def get_template(self, request, *args, **kwargs):
        standard_template = super(MultimediaSeriesPage, self).get_template(request, *args, **kwargs)
        if self.theme:
            return f'themes/{self.get_theme_dir()}/multimedia_series_page.html'
        return standard_template

    class Meta:
        verbose_name = 'Multimedia Series'
        verbose_name_plural = 'Multimedia Series'


class MultimediaListPagePromotionBlocks(Orderable):
    multimedia_list_page = ParentalKey(
        'multimedia.MultimediaListPage',
        related_name='promotion_blocks',
    )
    promotion_block = models.ForeignKey(
        'promotions.PromotionBlock',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Promotion Block',
    )

    panels = [
        FieldPanel(
            'promotion_block',
            ['promotions.PromotionBlock'],
        ),
    ]
