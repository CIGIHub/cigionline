from collections import OrderedDict
from bs4 import BeautifulSoup
from core.models import (
    BasicPageAbstract,
    ContentPage,
    FeatureablePageAbstract,
    FromTheArchivesPageAbstract,
    SearchablePageAbstract,
    ShareablePageAbstract,
    ThemeablePageAbstract,
)
from django.db.models.fields import CharField
from django.db import models
from modelcluster.fields import ParentalKey
from streams.blocks import (
    PodcastSubscribeButtonBlock,
    FeaturedEpisodeBlock,
    PodcastHostBlock,
    PodcastChapterBlock,
    PodcastGuestBlock,
    PodcastTranscriptBlock,
)
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.blocks import (
    CharBlock,
    IntegerBlock,
    StructBlock,
    TextBlock,
)
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page
from wagtail.search import index
import re


class MultimediaListPage(BasicPageAbstract, SearchablePageAbstract, Page):
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

    search_fields = Page.search_fields + BasicPageAbstract.search_fields + SearchablePageAbstract.search_fields

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
    length = models.CharField(
        blank=True,
        max_length=8,
        verbose_name='Length',
        help_text='| CIGI 3.0 field | The length of the multimedia source in minutes and seconds (e.g. 1:23).',
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
    podcast_recording_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Recording Date',
    )
    podcast_episode = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Episode Number',
    )
    podcast_guests = StreamField(
        [
            ('guest', CharBlock(required=True)),
            ('guest_page', PodcastGuestBlock()),
        ],
        blank=True,
        use_json_field=True,
        help_text='A list of guests for the podcast. If the guest has a page on the site, you can link to it here.',
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
    short_description = RichTextField(
        blank=True,
        null=False,
        features=['bold', 'italic', 'link'],
    )
    podcast_chapters = StreamField(
        [
            ('podcast_chapter', PodcastChapterBlock())
        ],
        blank=True,
        verbose_name='Podcast Chapters',
        help_text='A list of chapters for the podcast',
        use_json_field=True,
    )
    transcript = StreamField(
        [
            BasicPageAbstract.body_accordion_block,
            BasicPageAbstract.body_read_more_block,
            ('transcript_block', PodcastTranscriptBlock()),
        ],
        blank=True,
        use_json_field=True,
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
        use_json_field=True,
    )
    vimeo_url = models.URLField(
        blank=True,
        verbose_name='Vimeo URL',
        help_text='| CIGI 3.0 field | The URL of the multimedia source from Vimeo.',
    )
    youtube_id = models.CharField(
        blank=True,
        max_length=32,
        verbose_name='YouTube ID',
        help_text='Enter just the YouTube ID for this video. This is the series of letters and numbers found either at www.youtube.com/embed/[here], or www.youtube.com/watch?v=[here]. This is used for the video chaptering below.',
    )

    # Reference field for the Drupal-Wagtail migrator. Can be removed after.
    drupal_node_id = models.IntegerField(blank=True, null=True)

    @property
    def article_series_description(self):
        if self.article_series:
            if self.article_series.specific.series_videos_description:
                return self.article_series.specific.series_videos_description
            return self.article_series.specific.series_items_description
        return None

    def get_template(self, request, *args, **kwargs):
        standard_template = super(MultimediaPage, self).get_template(request, *args, **kwargs)
        if self.theme:
            return f'themes/{self.get_theme_dir()}/multimedia_page.html'
        return standard_template

    def podcast_episode_minutes(self):
        return int(self.podcast_audio_duration.split(':')[0])

    def next_episode(self):
        if self.podcast_episode is None:
            return None
        next_episode_number = self.podcast_episode + 1
        season_number = self.podcast_season
        return MultimediaPage.objects.filter(multimedia_series=self.multimedia_series, podcast_episode=next_episode_number, podcast_season=season_number).first()

    def get_transcript(self):
        soup = BeautifulSoup(self.transcript[0].value['text'].source, 'html.parser')
        parsed_transcript = []
        paragraphs = soup.find_all('p')
        pattern = r"(?P<name>.*?)\s*\((?P<role>host|guest)\):"
        current_speaker = None
        current_role = None
        current_text = []

        for para in paragraphs:
            text = para.get_text(strip=True)
            match = re.match(pattern, text, flags=re.IGNORECASE)
            if match:
                if current_speaker:
                    parsed_transcript.append({
                        'name': current_speaker,
                        'role': current_role,
                        'text': ''.join(current_text)
                    })
                current_speaker = match.group('name').strip()
                current_role = match.group('role').strip()
                current_text = []
            else:
                current_text.append(str(para))

        if current_speaker:
            parsed_transcript.append({
                'name': current_speaker,
                'role': current_role,
                'text': ''.join(current_text)
            })

        return parsed_transcript

    content_panels = [
        BasicPageAbstract.title_panel,
        MultiFieldPanel(
            [
                FieldPanel('short_description'),
                FieldPanel('body'),
            ],
            heading='Body',
            classname='collapsible collapsed'
        ),
        MultiFieldPanel(
            [
                FieldPanel('multimedia_type'),
                FieldPanel('publishing_date'),
                FieldPanel('multimedia_url'),
                FieldPanel('vimeo_url'),
                FieldPanel('length'),
            ],
            heading='General Information',
            classname='collapsible collapsed',
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
                FieldPanel('video_chapters'),
            ],
            heading='Video Chapters',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('transcript'),
            ],
            heading='Transcript',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('podcast_subtitle'),
                FieldPanel('podcast_season'),
                FieldPanel('podcast_episode'),
                FieldPanel('podcast_guests'),
                FieldPanel('podcast_chapters'),
                MultiFieldPanel(
                    [
                        FieldPanel('podcast_audio_url'),
                        FieldPanel('podcast_audio_duration'),
                        FieldPanel('podcast_audio_file_size'),
                        FieldPanel('podcast_recording_date'),
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
                FieldPanel('image_hero'),
                FieldPanel('image_banner'),
                FieldPanel('image_square'),
                FieldPanel('image_poster'),
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
                FieldPanel('countries'),
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
    credits = RichTextField(
        blank=True,
        null=False,
        features=['bold', 'italic', 'link'],
    )
    featured_episodes = StreamField(
        [
            ('featured_episode', FeaturedEpisodeBlock()),
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
    podcast_season_tagline = CharField(blank=True, null=True, max_length=256)
    podcast_subscribe_buttons = StreamField([
        ('podcast_subscribe_button', PodcastSubscribeButtonBlock())
    ],
        blank=True,
        verbose_name='Podcast Subscribe Buttons',
        help_text='A list of subscribe links to various podcast providers',
        use_json_field=True,
    )
    podcast_hosts = StreamField([
        ('podcast_host', PodcastHostBlock())
    ],
        blank=True,
        verbose_name='Podcast Hosts',
        help_text='Hosts of the podcast',
        use_json_field=True
    )
    podcast_live = models.BooleanField(default=False)

    @property
    def series_seasons_big_tech(self):
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
    def series_seasons(self):
        episode_filter = {'multimedia_series': self}
        series_episodes = MultimediaPage.objects.filter(**episode_filter).order_by('-publishing_date')
        seasons = {}
        for episode in series_episodes:
            season = episode.specific.podcast_season or 0
            if season not in seasons:
                seasons[season] = {'published': [], 'unpublished': []}
            (seasons[season]['published'] if episode.live else seasons[season]['unpublished']).append(episode)

        return OrderedDict(sorted(seasons.items(), key=lambda x: x[0]))

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
                FieldPanel('credits'),
            ],
            heading='General Information',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('image_hero'),
                FieldPanel('image_banner'),
                FieldPanel('image_poster'),
            ],
            heading='Images',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('image_logo'),
                FieldPanel('podcast_hosts'),
                FieldPanel('podcast_season_tagline'),
                FieldPanel('podcast_subscribe_buttons'),
                FieldPanel('podcast_live'),
            ],
            heading='Podcast Details',
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
        ),
    ]
